"""Coaching handler service (AGT-014).

Provides supportive conversational coaching for users who are stuck or struggling.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, UTC

from pydantic import BaseModel
import structlog

from app.ai import AIProvider, Message, get_ai_provider
from app.prompts.registry import get_prompt

logger = structlog.get_logger()


@dataclass
class CoachingMessage:
    """A single message in a coaching conversation."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CoachingConversation:
    """Manages state for a coaching conversation.

    Maintains conversation history and optional task context.
    """

    user_id: str
    task_id: str | None = None
    task_title: str | None = None
    messages: list[CoachingMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        self.messages.append(CoachingMessage(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation."""
        self.messages.append(CoachingMessage(role="assistant", content=content))

    def get_history(self, limit: int = 10) -> list[Message]:
        """Get recent conversation history as AI messages.

        Args:
            limit: Maximum number of messages to include.

        Returns:
            List of Message objects for AI context.
        """
        recent = self.messages[-limit:] if len(self.messages) > limit else self.messages
        return [Message(role=m.role, content=m.content) for m in recent]


class CoachingResponse(BaseModel):
    """Response from the coaching handler."""

    content: str
    suggested_action: str | None = None


class CoachingService:
    """Service for empathetic coaching conversations.

    Provides supportive responses for users who are:
    - Feeling stuck or paralyzed
    - Overwhelmed by tasks
    - Experiencing avoidance or procrastination
    - Needing emotional validation

    Key principles:
    1. VALIDATE first - acknowledge feelings without minimizing
    2. NORMALIZE - "This is hard for everyone"
    3. TINY STEP - suggest smallest possible action
    4. NO SHAME - never imply they should have done better
    """

    def __init__(self, ai_provider: AIProvider | None = None):
        """Initialize the coaching service.

        Args:
            ai_provider: AI provider for responses. Defaults to configured provider.
        """
        self.ai = ai_provider or get_ai_provider()
        # In-memory conversation storage (would use database in production)
        self._conversations: dict[str, CoachingConversation] = {}

    def get_or_create_conversation(
        self,
        user_id: str,
        task_id: str | None = None,
        task_title: str | None = None,
    ) -> CoachingConversation:
        """Get existing conversation or create a new one.

        Args:
            user_id: User identifier.
            task_id: Optional task being discussed.
            task_title: Optional task title for context.

        Returns:
            CoachingConversation instance.
        """
        # Key includes task_id if present for task-specific coaching
        key = f"{user_id}:{task_id}" if task_id else user_id

        if key not in self._conversations:
            self._conversations[key] = CoachingConversation(
                user_id=user_id,
                task_id=task_id,
                task_title=task_title,
            )
            logger.debug(
                "Created new coaching conversation",
                user_id=user_id,
                task_id=task_id,
            )

        return self._conversations[key]

    async def process(
        self,
        message: str,
        user_id: str,
        task_id: str | None = None,
        task_title: str | None = None,
    ) -> str:
        """Process a coaching message and return response.

        Args:
            message: User's message.
            user_id: User identifier.
            task_id: Optional task being discussed.
            task_title: Optional task title for context.

        Returns:
            Coaching response text.
        """
        conversation = self.get_or_create_conversation(user_id, task_id, task_title)
        conversation.add_user_message(message)

        # Build context
        system = self._build_system_prompt(task_title)
        history = conversation.get_history()

        try:
            response = await self.ai.complete(
                messages=history,
                system=system,
                max_tokens=500,
            )

            content = response.content
            conversation.add_assistant_message(content)

            logger.info(
                "Coaching response generated",
                user_id=user_id,
                message_count=len(conversation.messages),
            )

            return content
        except Exception as e:
            logger.error("Coaching failed", error=str(e), user_id=user_id)
            # Return empathetic fallback
            return self._get_fallback_response()

    async def stream(
        self,
        message: str,
        user_id: str,
        task_id: str | None = None,
        task_title: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a coaching response.

        Args:
            message: User's message.
            user_id: User identifier.
            task_id: Optional task being discussed.
            task_title: Optional task title for context.

        Yields:
            Text chunks as they are generated.
        """
        conversation = self.get_or_create_conversation(user_id, task_id, task_title)
        conversation.add_user_message(message)

        system = self._build_system_prompt(task_title)
        history = conversation.get_history()

        full_response = ""
        try:
            async for chunk in self.ai.stream(
                messages=history,
                system=system,
                max_tokens=500,
            ):
                full_response += chunk
                yield chunk

            conversation.add_assistant_message(full_response)
            logger.info(
                "Coaching stream complete",
                user_id=user_id,
                response_length=len(full_response),
            )
        except Exception as e:
            logger.error("Coaching stream failed", error=str(e))
            yield self._get_fallback_response()

    def clear_conversation(self, user_id: str, task_id: str | None = None) -> None:
        """Clear a conversation's history.

        Args:
            user_id: User identifier.
            task_id: Optional task identifier.
        """
        key = f"{user_id}:{task_id}" if task_id else user_id
        if key in self._conversations:
            del self._conversations[key]
            logger.debug("Cleared coaching conversation", user_id=user_id)

    def _build_system_prompt(self, task_title: str | None = None) -> str:
        """Build the system prompt with optional task context.

        Args:
            task_title: Optional task being discussed.

        Returns:
            System prompt string.
        """
        prompt = get_prompt("coaching")
        system = prompt.content

        if task_title:
            system += f"\n\nContext: The user is working on '{task_title}'."

        return system

    def _get_fallback_response(self) -> str:
        """Get a fallback response when AI fails."""
        return (
            "I hear you - this sounds really challenging. Sometimes our brains "
            "just need a moment. What if we take a tiny step together? Even just "
            "naming one small thing you could do in the next 2 minutes counts as progress."
        )


def get_coaching_service() -> CoachingService:
    """Factory function to get coaching service.

    Returns:
        CoachingService instance.
    """
    return CoachingService()
