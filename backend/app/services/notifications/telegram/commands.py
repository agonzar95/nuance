"""Telegram command handler.

Handles bot commands like /start, /help, /today, /status.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, Callable, Awaitable

import structlog

from app.clients.supabase import get_supabase_client
from app.config import settings
from app.services.notifications.providers.telegram import (
    TelegramNotificationProvider,
    get_telegram_provider,
)
from app.services.telegram_connection import get_telegram_connection_service

if TYPE_CHECKING:
    from app.services.notifications.telegram.handler import TelegramUpdate, TelegramHandler

logger = structlog.get_logger()


class TelegramCommandHandler:
    """Handles Telegram bot commands.

    Supported commands:
    - /start - Welcome message and account connection
    - /help - Show available commands
    - /today - Show today's plan
    - /status - Show current progress
    """

    def __init__(
        self,
        telegram_provider: TelegramNotificationProvider | None = None,
        handler: "TelegramHandler | None" = None,
    ):
        """Initialize command handler.

        Args:
            telegram_provider: Provider for sending responses.
            handler: Parent handler (for access to shared services).
        """
        self._telegram = telegram_provider or get_telegram_provider()
        self._handler = handler
        self._supabase = get_supabase_client()

        # Command registry
        self._commands: dict[str, Callable[["TelegramUpdate"], Awaitable[None]]] = {
            "/start": self.cmd_start,
            "/help": self.cmd_help,
            "/today": self.cmd_today,
            "/status": self.cmd_status,
        }

    async def handle(self, update: "TelegramUpdate") -> bool:
        """Handle a command.

        Args:
            update: The update containing the command.

        Returns:
            True if command was handled.
        """
        if not update.text or not update.text.startswith("/"):
            return False

        # Extract command (first word, lowercase)
        command = update.text.split()[0].lower()

        # Handle @botname suffix
        if "@" in command:
            command = command.split("@")[0]

        handler = self._commands.get(command)
        if handler:
            await handler(update)
            return True

        # Unknown command
        await self._telegram.send_message(
            update.chat_id,
            f"Unknown command: {command}\n\nUse /help to see available commands.",
        )
        return True

    async def cmd_start(self, update: "TelegramUpdate") -> None:
        """Handle /start command.

        Welcome message and connection link for new users.

        Args:
            update: The update.
        """
        user = await self._get_user_by_telegram(update.chat_id)

        if user:
            # Already connected
            await self._telegram.send_message(
                update.chat_id,
                f"Welcome back! You're connected.\n\n"
                "Just send me what's on your mind and I'll capture it as a task.",
            )
        else:
            # Generate connection token
            token = await self._generate_connection_token(update.chat_id)

            if token:
                app_url = settings.app_url.rstrip("/")
                link = f"{app_url}/settings/telegram?token={token}"

                await self._telegram.send_message(
                    update.chat_id,
                    "*Welcome to Nuance!*\n\n"
                    "I'm your Executive Function Prosthetic. "
                    "I help you capture tasks, break them down, and stay on track.\n\n"
                    f"To get started, connect your account:\n{link}\n\n"
                    "Or if you already have an account, go to Settings > Telegram in the app.",
                )
            else:
                await self._telegram.send_message(
                    update.chat_id,
                    "*Welcome to Nuance!*\n\n"
                    "To get started, please open the Nuance app and go to "
                    "Settings > Telegram to connect your account.",
                )

    async def cmd_help(self, update: "TelegramUpdate") -> None:
        """Handle /help command.

        Show available commands.

        Args:
            update: The update.
        """
        help_text = """*Available Commands*

/start - Connect or check your account
/today - See today's plan
/status - See your current progress
/help - Show this message

*Quick Capture*
Just send me a message to capture it as a task!

Examples:
• "Call mom about birthday party"
• "Review quarterly report by Friday"
• "Pick up groceries - milk, eggs, bread"

I'll extract the action and add it to your inbox."""

        await self._telegram.send_message(update.chat_id, help_text)

    async def cmd_today(self, update: "TelegramUpdate") -> None:
        """Handle /today command.

        Show today's plan.

        Args:
            update: The update.
        """
        user = await self._get_user_by_telegram(update.chat_id)

        if not user:
            await self._telegram.send_message(
                update.chat_id,
                "Please connect your account first with /start",
            )
            return

        # Get today's actions
        today = date.today().isoformat()
        try:
            response = (
                self._supabase.table("actions")
                .select("id, title, status, estimated_minutes, avoidance_weight")
                .eq("user_id", user["id"])
                .eq("planned_date", today)
                .order("position")
                .execute()
            )

            actions = response.data if response.data else []

            if not actions:
                await self._telegram.send_message(
                    update.chat_id,
                    "No plan set for today yet.\n\n"
                    "Open the app to plan your day, or just send me tasks to capture!",
                )
                return

            # Format task list
            task_lines = []
            done_count = 0
            for action in actions:
                if isinstance(action, dict):
                    status = action.get("status", "")
                    title = action.get("title", "Untitled")
                    est = action.get("estimated_minutes", 0)

                    if status == "done":
                        task_lines.append(f"✓ ~{title}~")
                        done_count += 1
                    else:
                        task_lines.append(f"○ {title} (~{est}min)")

            tasks_str = "\n".join(task_lines)
            total = len(actions)

            await self._telegram.send_message(
                update.chat_id,
                f"*Today's Plan* ({done_count}/{total} done)\n\n{tasks_str}",
            )

        except Exception as e:
            logger.error("Failed to get today's actions", error=str(e))
            await self._telegram.send_message(
                update.chat_id,
                "Sorry, I couldn't load your plan. Please try again.",
            )

    async def cmd_status(self, update: "TelegramUpdate") -> None:
        """Handle /status command.

        Show progress status.

        Args:
            update: The update.
        """
        user = await self._get_user_by_telegram(update.chat_id)

        if not user:
            await self._telegram.send_message(
                update.chat_id,
                "Please connect your account first with /start",
            )
            return

        # Get today's stats
        today = date.today().isoformat()
        try:
            response = (
                self._supabase.table("actions")
                .select("status, actual_minutes")
                .eq("user_id", user["id"])
                .eq("planned_date", today)
                .execute()
            )

            actions = response.data if response.data else []

            total = len(actions)
            completed = 0
            minutes_spent = 0

            for action in actions:
                if isinstance(action, dict):
                    if action.get("status") == "done":
                        completed += 1
                        minutes_spent += action.get("actual_minutes") or 0

            # Also count inbox items
            inbox_response = (
                self._supabase.table("actions")
                .select("id")
                .eq("user_id", user["id"])
                .eq("status", "inbox")
                .execute()
            )
            inbox_count = len(inbox_response.data) if inbox_response.data else 0

            # Format time
            hours = minutes_spent // 60
            mins = minutes_spent % 60
            time_str = f"{hours}h {mins}m" if hours else f"{mins}m"

            status_text = f"""*Today's Progress*

Planned: {total} tasks
Completed: {completed}/{total}
Time tracked: {time_str}

Inbox: {inbox_count} item{"s" if inbox_count != 1 else ""} waiting"""

            await self._telegram.send_message(update.chat_id, status_text)

        except Exception as e:
            logger.error("Failed to get status", error=str(e))
            await self._telegram.send_message(
                update.chat_id,
                "Sorry, I couldn't load your status. Please try again.",
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

    async def _generate_connection_token(self, chat_id: str) -> str | None:
        """Generate a token for connecting Telegram account.

        The token is stored temporarily and validated when
        the user completes the connection flow in the app.
        Tokens expire after 15 minutes.

        Args:
            chat_id: Telegram chat ID to associate.

        Returns:
            Connection token or None on failure.
        """
        try:
            service = get_telegram_connection_service()
            token = await service.create_token(chat_id)

            logger.info(
                "Connection token generated",
                chat_id=chat_id,
                token_prefix=token[:8],
            )

            return token

        except Exception as e:
            logger.error("Failed to generate connection token", error=str(e))
            return None


def get_command_handler() -> TelegramCommandHandler:
    """Factory function for dependency injection.

    Returns:
        Configured TelegramCommandHandler instance.
    """
    return TelegramCommandHandler()
