"""Intent classification service (AGT-013).

Classifies user messages into intents: capture, coaching, or command.
"""

from enum import Enum

from pydantic import BaseModel, Field
import structlog

from app.ai import AIProvider, get_ai_provider
from app.prompts.registry import get_prompt

logger = structlog.get_logger()


class Intent(str, Enum):
    """User intent categories."""

    CAPTURE = "capture"    # Adding/managing tasks
    COACHING = "coaching"  # Emotional support, feeling stuck
    COMMAND = "command"    # System commands (/help, /start)


class IntentResult(BaseModel):
    """Result of intent classification."""

    intent: Intent = Field(
        ...,
        description="Classified intent type",
    )
    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence in the classification",
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of why this intent was chosen",
    )


# Action verbs that strongly indicate capture intent
_ACTION_STARTERS = frozenset([
    "buy", "call", "send", "email", "write", "do", "finish", "complete",
    "submit", "schedule", "book", "order", "pick", "get", "make", "create",
    "fix", "update", "review", "prepare", "clean", "organize", "pay",
    "cancel", "renew", "return", "check", "reply", "respond", "follow",
])

# Emotional/stuck indicators for coaching intent
_COACHING_SIGNALS = frozenset([
    "can't", "cannot", "stuck", "overwhelmed", "anxious", "scared",
    "don't know", "frustrated", "confused", "lost", "paralyzed",
    "procrastinating", "avoiding", "dreading", "hate", "impossible",
    "too much", "too hard", "help me", "what do i do", "why can't i",
])


class IntentClassifier:
    """Service for classifying user message intent.

    Uses fast heuristics for obvious cases and AI for ambiguous ones.
    Intents determine how the system responds:
    - CAPTURE: Route to action extraction
    - COACHING: Route to supportive conversation
    - COMMAND: Handle system commands
    """

    def __init__(self, ai_provider: AIProvider | None = None):
        """Initialize the intent classifier.

        Args:
            ai_provider: AI provider for ambiguous cases. Defaults to configured provider.
        """
        self.ai = ai_provider or get_ai_provider()

    async def classify(self, text: str) -> IntentResult:
        """Classify the intent of a user message.

        Args:
            text: User message text.

        Returns:
            IntentResult with classified intent and confidence.
        """
        text_stripped = text.strip()
        text_lower = text_stripped.lower()

        # Fast path: commands
        if text_stripped.startswith("/"):
            logger.debug("Intent: command (prefix)", text=text_stripped[:50])
            return IntentResult(
                intent=Intent.COMMAND,
                confidence=1.0,
                reasoning="Message starts with /",
            )

        # Fast path: obvious action verbs at start
        first_word = text_lower.split()[0] if text_lower else ""
        if first_word in _ACTION_STARTERS:
            logger.debug("Intent: capture (action verb)", text=text_stripped[:50])
            return IntentResult(
                intent=Intent.CAPTURE,
                confidence=0.95,
                reasoning=f"Starts with action verb: {first_word}",
            )

        # Fast path: "add:", "todo:", etc.
        if any(text_lower.startswith(p) for p in ["add:", "add ", "todo:", "task:"]):
            logger.debug("Intent: capture (add prefix)", text=text_stripped[:50])
            return IntentResult(
                intent=Intent.CAPTURE,
                confidence=0.98,
                reasoning="Explicit add/todo prefix",
            )

        # Check for coaching signals
        coaching_match = any(signal in text_lower for signal in _COACHING_SIGNALS)
        if coaching_match:
            # Strong emotional signals go straight to coaching
            logger.debug("Intent: coaching (signals detected)", text=text_stripped[:50])
            return IntentResult(
                intent=Intent.COACHING,
                confidence=0.90,
                reasoning="Emotional/stuck signals detected",
            )

        # Ambiguous case: use AI classification
        return await self._ai_classify(text)

    async def _ai_classify(self, text: str) -> IntentResult:
        """Use AI to classify ambiguous messages.

        Args:
            text: User message text.

        Returns:
            IntentResult from AI classification.
        """
        prompt = get_prompt("intent")
        logger.debug(
            "AI classifying intent",
            text=text[:100],
            prompt_version=prompt.version,
        )

        try:
            # Simple completion, not extraction - just need the intent name
            from app.ai.base import Message

            response = await self.ai.complete(
                messages=[Message(role="user", content=text)],
                system=prompt.content,
                max_tokens=20,
            )

            intent_str = response.content.strip().upper()

            # Parse response into Intent enum
            try:
                intent = Intent[intent_str]
            except KeyError:
                # Default to capture if response is unexpected
                logger.warning(
                    "Unexpected intent response",
                    response=response.content,
                    defaulting_to="capture",
                )
                intent = Intent.CAPTURE

            logger.info(
                "AI classified intent",
                text=text[:50],
                intent=intent.value,
            )

            return IntentResult(
                intent=intent,
                confidence=0.85,
                reasoning=f"AI classified as {intent.value}",
            )
        except Exception as e:
            logger.error("AI intent classification failed", error=str(e))
            # Default to capture on failure - safer to try extraction
            return IntentResult(
                intent=Intent.CAPTURE,
                confidence=0.5,
                reasoning=f"Classification failed, defaulting to capture: {e}",
            )


def get_intent_classifier() -> IntentClassifier:
    """Factory function to get intent classifier.

    Returns:
        IntentClassifier instance.
    """
    return IntentClassifier()
