"""Intent-based request router (AGT-002).

Routes user messages to the appropriate handler based on classified intent.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
import structlog

from app.services.intent import Intent, IntentClassifier, IntentResult, get_intent_classifier
from app.services.extraction_orchestrator import (
    ExtractionOrchestrator,
    OrchestrationResult,
    get_extraction_orchestrator,
)
from app.services.coaching import CoachingService, get_coaching_service

logger = structlog.get_logger()


# ============================================================================
# Response Models
# ============================================================================


class CommandResponse(BaseModel):
    """Response from a command handler."""

    command: str = Field(..., description="The command that was executed")
    message: str = Field(..., description="Response message")
    data: dict[str, Any] | None = Field(default=None, description="Optional data payload")


class RouterResponse(BaseModel):
    """Unified response from the intent router."""

    intent: Intent = Field(..., description="The classified intent")
    intent_confidence: float = Field(..., description="Confidence of intent classification")
    response_type: str = Field(..., description="Type of response: capture|coaching|command")

    # Response content (one of these will be populated)
    extraction: OrchestrationResult | None = Field(
        default=None, description="Extraction result for CAPTURE intent"
    )
    coaching_response: str | None = Field(
        default=None, description="Coaching response for COACHING intent"
    )
    command_response: CommandResponse | None = Field(
        default=None, description="Command response for COMMAND intent"
    )


# ============================================================================
# Command Handler
# ============================================================================


class CommandHandler:
    """Handles system commands (/start, /help, etc.)."""

    def __init__(self) -> None:
        """Initialize the command handler."""
        self._user_contexts: dict[str, dict[str, Any]] = {}

    async def process(self, text: str, user_id: str) -> CommandResponse:
        """Process a command message.

        Args:
            text: Command text (e.g., "/help").
            user_id: User identifier.

        Returns:
            CommandResponse with the result.
        """
        # Parse command and arguments
        parts = text.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        logger.info("Processing command", command=command, user_id=user_id)

        # Route to handler
        match command:
            case "/start":
                return await self._handle_start(user_id, args)
            case "/help":
                return await self._handle_help(user_id, args)
            case "/clear":
                return await self._handle_clear(user_id, args)
            case "/status":
                return await self._handle_status(user_id, args)
            case _:
                return CommandResponse(
                    command=command,
                    message=f"Unknown command: {command}. Type /help for available commands.",
                )

    async def _handle_start(self, user_id: str, args: str) -> CommandResponse:
        """Handle /start command - initialize or reset."""
        return CommandResponse(
            command="/start",
            message=(
                "Welcome to Nuance! I'm your executive function assistant.\n\n"
                "You can:\n"
                "- Tell me about tasks (e.g., 'Buy groceries and call mom')\n"
                "- Talk when you're stuck (e.g., 'I can't focus today')\n"
                "- Use /help for more commands\n\n"
                "What would you like to capture or talk about?"
            ),
        )

    async def _handle_help(self, user_id: str, args: str) -> CommandResponse:
        """Handle /help command - show available commands."""
        return CommandResponse(
            command="/help",
            message=(
                "Available commands:\n\n"
                "/start - Start fresh or see welcome message\n"
                "/help - Show this help message\n"
                "/clear - Clear conversation history\n"
                "/status - Check your current status\n\n"
                "Or just tell me:\n"
                "- Tasks to capture: 'I need to call mom and buy groceries'\n"
                "- When you're stuck: 'I can't focus' or 'I'm overwhelmed'"
            ),
        )

    async def _handle_clear(self, user_id: str, args: str) -> CommandResponse:
        """Handle /clear command - clear conversation context."""
        if user_id in self._user_contexts:
            del self._user_contexts[user_id]
        return CommandResponse(
            command="/clear",
            message="Conversation cleared. What would you like to work on?",
        )

    async def _handle_status(self, user_id: str, args: str) -> CommandResponse:
        """Handle /status command - show current state."""
        return CommandResponse(
            command="/status",
            message="Status check - all systems operational.",
            data={"user_id": user_id, "services": ["capture", "coaching", "commands"]},
        )


def get_command_handler() -> CommandHandler:
    """Factory function for command handler."""
    return CommandHandler()


# ============================================================================
# Intent Router
# ============================================================================


class IntentRouter:
    """Routes user messages to appropriate handlers based on intent.

    The router:
    1. Classifies the intent using IntentClassifier
    2. Dispatches to the appropriate handler:
       - CAPTURE: ExtractionOrchestrator (for task capture)
       - COACHING: CoachingService (for emotional support)
       - COMMAND: CommandHandler (for system commands)
    3. Returns a unified response
    """

    def __init__(
        self,
        classifier: IntentClassifier | None = None,
        extraction: ExtractionOrchestrator | None = None,
        coaching: CoachingService | None = None,
        command: CommandHandler | None = None,
    ):
        """Initialize the intent router.

        Args:
            classifier: Intent classifier service.
            extraction: Extraction orchestrator for CAPTURE intent.
            coaching: Coaching service for COACHING intent.
            command: Command handler for COMMAND intent.
        """
        self.classifier = classifier or get_intent_classifier()
        self.extraction = extraction or get_extraction_orchestrator()
        self.coaching = coaching or get_coaching_service()
        self.command = command or get_command_handler()

    async def route(
        self,
        text: str,
        user_id: str,
        task_id: str | None = None,
        task_title: str | None = None,
    ) -> RouterResponse:
        """Route a message to the appropriate handler.

        Args:
            text: User message text.
            user_id: User identifier.
            task_id: Optional task context (for coaching).
            task_title: Optional task title (for coaching context).

        Returns:
            RouterResponse with the appropriate result.
        """
        if not text or not text.strip():
            logger.warning("Empty message received", user_id=user_id)
            return RouterResponse(
                intent=Intent.CAPTURE,
                intent_confidence=0.0,
                response_type="capture",
                extraction=OrchestrationResult(
                    actions=[],
                    raw_input="",
                    overall_confidence=0.0,
                    needs_validation=True,
                ),
            )

        # Step 1: Classify intent
        intent_result = await self.classifier.classify(text)

        logger.info(
            "Intent classified",
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            user_id=user_id,
        )

        # Step 2: Route to appropriate handler
        match intent_result.intent:
            case Intent.CAPTURE:
                return await self._handle_capture(text, user_id, intent_result)
            case Intent.COACHING:
                return await self._handle_coaching(
                    text, user_id, intent_result, task_id, task_title
                )
            case Intent.COMMAND:
                return await self._handle_command(text, user_id, intent_result)
            case _:
                # Fallback to capture for safety
                logger.warning(
                    "Unknown intent, defaulting to capture",
                    intent=intent_result.intent,
                )
                return await self._handle_capture(text, user_id, intent_result)

    async def route_with_intent(
        self,
        text: str,
        intent: Intent,
        user_id: str,
        task_id: str | None = None,
        task_title: str | None = None,
    ) -> RouterResponse:
        """Route a message with a pre-classified intent.

        Useful when intent has already been determined or for testing.

        Args:
            text: User message text.
            intent: Pre-classified intent.
            user_id: User identifier.
            task_id: Optional task context.
            task_title: Optional task title.

        Returns:
            RouterResponse with the appropriate result.
        """
        intent_result = IntentResult(
            intent=intent,
            confidence=1.0,
            reasoning="Pre-classified intent",
        )

        match intent:
            case Intent.CAPTURE:
                return await self._handle_capture(text, user_id, intent_result)
            case Intent.COACHING:
                return await self._handle_coaching(
                    text, user_id, intent_result, task_id, task_title
                )
            case Intent.COMMAND:
                return await self._handle_command(text, user_id, intent_result)
            case _:
                return await self._handle_capture(text, user_id, intent_result)

    async def stream_coaching(
        self,
        text: str,
        user_id: str,
        task_id: str | None = None,
        task_title: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a coaching response.

        For real-time streaming of coaching conversations.

        Args:
            text: User message text.
            user_id: User identifier.
            task_id: Optional task context.
            task_title: Optional task title.

        Yields:
            Text chunks as they are generated.
        """
        async for chunk in self.coaching.stream(
            message=text,
            user_id=user_id,
            task_id=task_id,
            task_title=task_title,
        ):
            yield chunk

    async def _handle_capture(
        self,
        text: str,
        user_id: str,
        intent_result: IntentResult,
    ) -> RouterResponse:
        """Handle CAPTURE intent - extract actions from text.

        Args:
            text: User message text.
            user_id: User identifier.
            intent_result: Classification result.

        Returns:
            RouterResponse with extraction result.
        """
        logger.debug("Routing to extraction", user_id=user_id)

        extraction_result = await self.extraction.extract(text)

        logger.info(
            "Capture complete",
            user_id=user_id,
            action_count=len(extraction_result.actions),
            confidence=extraction_result.overall_confidence,
        )

        return RouterResponse(
            intent=Intent.CAPTURE,
            intent_confidence=intent_result.confidence,
            response_type="capture",
            extraction=extraction_result,
        )

    async def _handle_coaching(
        self,
        text: str,
        user_id: str,
        intent_result: IntentResult,
        task_id: str | None,
        task_title: str | None,
    ) -> RouterResponse:
        """Handle COACHING intent - provide supportive response.

        Args:
            text: User message text.
            user_id: User identifier.
            intent_result: Classification result.
            task_id: Optional task being discussed.
            task_title: Optional task title for context.

        Returns:
            RouterResponse with coaching response.
        """
        logger.debug("Routing to coaching", user_id=user_id, task_id=task_id)

        response = await self.coaching.process(
            message=text,
            user_id=user_id,
            task_id=task_id,
            task_title=task_title,
        )

        logger.info(
            "Coaching complete",
            user_id=user_id,
            response_length=len(response),
        )

        return RouterResponse(
            intent=Intent.COACHING,
            intent_confidence=intent_result.confidence,
            response_type="coaching",
            coaching_response=response,
        )

    async def _handle_command(
        self,
        text: str,
        user_id: str,
        intent_result: IntentResult,
    ) -> RouterResponse:
        """Handle COMMAND intent - process system command.

        Args:
            text: Command text.
            user_id: User identifier.
            intent_result: Classification result.

        Returns:
            RouterResponse with command response.
        """
        logger.debug("Routing to command handler", user_id=user_id)

        response = await self.command.process(text, user_id)

        logger.info(
            "Command processed",
            user_id=user_id,
            command=response.command,
        )

        return RouterResponse(
            intent=Intent.COMMAND,
            intent_confidence=intent_result.confidence,
            response_type="command",
            command_response=response,
        )


def get_intent_router() -> IntentRouter:
    """Factory function for intent router.

    Returns:
        IntentRouter instance.
    """
    return IntentRouter()
