"""Telegram message handler.

Processes incoming Telegram updates and routes them appropriately.
"""

from dataclasses import dataclass
from typing import Any

import structlog

from app.clients.supabase import get_supabase_client
from app.services.notifications.providers.telegram import (
    TelegramNotificationProvider,
    get_telegram_provider,
)

logger = structlog.get_logger()


@dataclass
class TelegramUpdate:
    """Parsed Telegram update.

    Attributes:
        update_id: Unique update identifier.
        message_id: Message ID within the chat.
        chat_id: Chat where message was sent.
        text: Message text (if any).
        voice_file_id: Voice message file ID (if any).
        from_user: User who sent the message.
    """

    update_id: int
    message_id: int | None
    chat_id: str
    text: str | None
    voice_file_id: str | None
    from_user: dict[str, Any] | None


@dataclass
class ProcessResult:
    """Result of processing a Telegram message.

    Attributes:
        success: Whether processing succeeded.
        action_id: ID of created action (if any).
        action_title: Title of created action (if any).
        error: Error message (if failed).
    """

    success: bool
    action_id: str | None = None
    action_title: str | None = None
    error: str | None = None


class TelegramHandler:
    """Handles incoming Telegram messages.

    Routes messages to appropriate handlers:
    - Commands (/start, /help, etc.) -> TelegramCommandHandler
    - Text messages -> Extraction pipeline
    - Voice messages -> Transcription + Extraction
    """

    def __init__(
        self,
        telegram_provider: TelegramNotificationProvider | None = None,
    ):
        """Initialize handler.

        Args:
            telegram_provider: Provider for sending responses.
        """
        self._telegram = telegram_provider or get_telegram_provider()
        self._supabase = get_supabase_client()
        self._command_handler: "TelegramCommandHandler | None" = None

    def set_command_handler(self, handler: "TelegramCommandHandler") -> None:
        """Set the command handler.

        Args:
            handler: Command handler instance.
        """
        self._command_handler = handler

    async def process_update(self, raw_update: dict[str, Any]) -> None:
        """Process incoming Telegram update.

        Args:
            raw_update: Raw update from Telegram webhook.
        """
        update = self._parse_update(raw_update)
        if not update:
            logger.debug("Could not parse update", raw=raw_update)
            return

        # Check for commands first
        if update.text and update.text.startswith("/"):
            if self._command_handler:
                await self._command_handler.handle(update)
            else:
                await self._handle_unknown_command(update)
            return

        # Look up user by chat ID
        user = await self._get_user_by_telegram(update.chat_id)

        if not user:
            # Unknown user - prompt to connect
            await self._telegram.send_message(
                update.chat_id,
                "I don't recognize you yet! Please connect your Telegram account "
                "in the Nuance app settings to start capturing tasks here.",
            )
            return

        # Process voice message if present
        text = update.text
        if update.voice_file_id and not text:
            text = await self._transcribe_voice(update.voice_file_id)
            if not text:
                await self._telegram.send_message(
                    update.chat_id,
                    "Sorry, I couldn't transcribe that voice message. "
                    "Please try again or send a text message.",
                )
                return

        if not text:
            logger.debug("No text to process", update_id=update.update_id)
            return

        # Process as capture input
        result = await self._process_capture(user["id"], text, update.chat_id)

        if result.success and result.action_title:
            await self._telegram.send_message(
                update.chat_id,
                f"Got it! Added: *{result.action_title}*",
            )
        elif result.error:
            await self._telegram.send_message(
                update.chat_id,
                "Sorry, I couldn't process that. Try again?",
            )

    def _parse_update(self, raw: dict[str, Any]) -> TelegramUpdate | None:
        """Parse raw update into TelegramUpdate.

        Args:
            raw: Raw update from Telegram.

        Returns:
            Parsed update or None if invalid.
        """
        message = raw.get("message", {})
        if not message:
            # Could be callback_query or other update type
            return None

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        if not chat_id:
            return None

        # Check for voice message
        voice = message.get("voice", {})
        voice_file_id = voice.get("file_id") if voice else None

        return TelegramUpdate(
            update_id=raw.get("update_id", 0),
            message_id=message.get("message_id"),
            chat_id=str(chat_id),
            text=message.get("text"),
            voice_file_id=voice_file_id,
            from_user=message.get("from"),
        )

    async def _get_user_by_telegram(self, chat_id: str) -> dict[str, Any] | None:
        """Look up user by Telegram chat ID.

        Args:
            chat_id: Telegram chat ID.

        Returns:
            User data or None if not found.
        """
        try:
            response = (
                self._supabase.table("profiles")
                .select("id")
                .eq("telegram_chat_id", chat_id)
                .single()
                .execute()
            )

            if response.data and isinstance(response.data, dict):
                return response.data
            return None

        except Exception as e:
            logger.error("Failed to look up user", chat_id=chat_id, error=str(e))
            return None

    async def _transcribe_voice(self, file_id: str) -> str | None:
        """Transcribe voice message.

        Args:
            file_id: Telegram file ID for voice message.

        Returns:
            Transcribed text or None on failure.
        """
        try:
            from app.services.transcription import TranscriptionService

            service = TranscriptionService()
            result = await service.transcribe_telegram_voice(file_id)
            return result

        except Exception as e:
            logger.error("Voice transcription failed", file_id=file_id, error=str(e))
            return None

    async def _process_capture(
        self,
        user_id: str,
        text: str,
        chat_id: str,
    ) -> ProcessResult:
        """Process text as capture input.

        Routes to extraction pipeline and saves resulting action.

        Args:
            user_id: User ID.
            text: Text to process.
            chat_id: Telegram chat ID (for context).

        Returns:
            ProcessResult with outcome.
        """
        try:
            # Use the extraction orchestrator
            from app.services.extraction_orchestrator import get_extraction_orchestrator

            orchestrator = get_extraction_orchestrator()
            result = await orchestrator.extract(text)

            if result.actions and len(result.actions) > 0:
                # Save the first action to database
                action = result.actions[0]
                action_data = {
                    "user_id": user_id,
                    "title": action.title,
                    "raw_input": text,
                    "status": "inbox",
                    "complexity": action.complexity.value if action.complexity else "atomic",
                    "avoidance_weight": action.avoidance_weight or 1,
                    "estimated_minutes": action.estimated_minutes or 15,
                }

                insert_response = (
                    self._supabase.table("actions")
                    .insert(action_data)
                    .execute()
                )

                if insert_response.data and isinstance(insert_response.data, list):
                    first_item = insert_response.data[0]
                    if isinstance(first_item, dict):
                        action_id = first_item.get("id")
                        return ProcessResult(
                            success=True,
                            action_id=str(action_id) if action_id else None,
                            action_title=action.title,
                        )

            return ProcessResult(
                success=False,
                error="No actions extracted",
            )

        except Exception as e:
            logger.error("Capture processing failed", error=str(e))
            return ProcessResult(
                success=False,
                error=str(e),
            )

    async def _handle_unknown_command(self, update: TelegramUpdate) -> None:
        """Handle unknown command when no command handler is set.

        Args:
            update: The update with the command.
        """
        await self._telegram.send_message(
            update.chat_id,
            "Sorry, I don't understand that command. Try /help to see available commands.",
        )


# Import TelegramCommandHandler at runtime to avoid circular imports
from app.services.notifications.telegram.commands import TelegramCommandHandler


def get_telegram_handler() -> TelegramHandler:
    """Factory function for dependency injection.

    Returns:
        Configured TelegramHandler with command handler attached.
    """
    handler = TelegramHandler()
    command_handler = TelegramCommandHandler(handler=handler)
    handler.set_command_handler(command_handler)
    return handler
