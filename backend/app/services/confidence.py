"""Confidence scoring service (AGT-011).

Assesses extraction confidence to determine when user clarification is needed.
"""

from pydantic import BaseModel, Field
import structlog

from app.ai import AIProvider, get_ai_provider
from app.prompts.registry import get_prompt
from app.services.extraction import ExtractedAction

logger = structlog.get_logger()


class ConfidenceAnalysis(BaseModel):
    """Result of confidence scoring for an extraction."""

    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 (low) to 1.0 (high)",
    )
    ambiguities: list[str] = Field(
        default_factory=list,
        description="Aspects that may need user clarification",
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of the confidence score",
    )


# Action verbs that indicate high confidence
_STRONG_ACTION_VERBS = frozenset([
    "buy", "call", "send", "email", "write", "submit", "schedule",
    "book", "order", "pay", "cancel", "return", "pick", "get",
    "create", "fix", "update", "review", "clean", "organize",
])

# Vague language patterns that reduce confidence
_VAGUE_PATTERNS = frozenset([
    "that thing", "stuff", "whatever", "something", "somehow",
    "the thing", "that project", "those things", "misc",
])


class ConfidenceService:
    """Service for scoring extraction confidence.

    High confidence (0.9-1.0): Clear action, specific object
    Medium confidence (0.7-0.9): Implied action, some ambiguity
    Low confidence (0.0-0.7): Vague language, unclear intent
    """

    def __init__(self, ai_provider: AIProvider | None = None):
        """Initialize the confidence scoring service.

        Args:
            ai_provider: AI provider for complex cases. Defaults to configured provider.
        """
        self.ai = ai_provider or get_ai_provider()

    async def score(self, action: ExtractedAction, raw_input: str) -> ConfidenceAnalysis:
        """Score confidence for an extracted action.

        Args:
            action: The extracted action to score.
            raw_input: Original user input text.

        Returns:
            ConfidenceAnalysis with score and any ambiguities.
        """
        # Quick heuristic scoring
        title_lower = action.title.lower()
        input_lower = raw_input.lower()
        ambiguities: list[str] = []

        # Check for strong action verb at start
        first_word = title_lower.split()[0] if title_lower else ""
        has_action_verb = first_word in _STRONG_ACTION_VERBS

        # Check for vague patterns
        has_vague_pattern = any(pattern in input_lower for pattern in _VAGUE_PATTERNS)
        if has_vague_pattern:
            ambiguities.append("Input contains vague language")

        # Check title length (very short titles are often unclear)
        if len(action.title) < 5:
            ambiguities.append("Task title is very short")

        # Check for question marks (might be asking, not task capture)
        if "?" in raw_input:
            ambiguities.append("Input contains question - may not be a task")

        # Calculate base confidence
        base_confidence = 0.8

        if has_action_verb:
            base_confidence += 0.1
        if has_vague_pattern:
            base_confidence -= 0.3
        if len(action.title) < 5:
            base_confidence -= 0.1
        if "?" in raw_input:
            base_confidence -= 0.15

        # Check time estimate reasonableness
        if action.estimated_minutes < 5 or action.estimated_minutes > 240:
            base_confidence -= 0.1
            ambiguities.append("Time estimate may need adjustment")

        # Clamp to valid range
        confidence = max(0.0, min(1.0, base_confidence))

        # For low-confidence cases, use AI for deeper analysis
        if confidence < 0.6 and not has_vague_pattern:
            return await self._ai_score(action, raw_input, ambiguities)

        reasoning = self._generate_reasoning(
            has_action_verb, has_vague_pattern, len(ambiguities)
        )

        logger.info(
            "Confidence scored",
            title=action.title[:50],
            confidence=confidence,
            ambiguity_count=len(ambiguities),
        )

        return ConfidenceAnalysis(
            confidence=round(confidence, 2),
            ambiguities=ambiguities,
            reasoning=reasoning,
        )

    async def _ai_score(
        self,
        action: ExtractedAction,
        raw_input: str,
        existing_ambiguities: list[str],
    ) -> ConfidenceAnalysis:
        """Use AI for deeper confidence analysis.

        Args:
            action: The extracted action.
            raw_input: Original input text.
            existing_ambiguities: Already detected ambiguities.

        Returns:
            ConfidenceAnalysis from AI.
        """
        prompt = get_prompt("confidence")

        text = f"Action: {action.title}\nOriginal input: {raw_input}"

        try:
            result = await self.ai.extract(
                text=text,
                schema=ConfidenceAnalysis,
                system=prompt.content,
            )

            # Merge existing ambiguities
            all_ambiguities = list(set(existing_ambiguities + result.ambiguities))

            logger.info(
                "AI confidence scored",
                title=action.title[:50],
                confidence=result.confidence,
            )

            return ConfidenceAnalysis(
                confidence=result.confidence,
                ambiguities=all_ambiguities,
                reasoning=result.reasoning,
            )
        except ValueError as e:
            logger.error("AI confidence scoring failed", error=str(e))
            # Fall back to heuristic result
            return ConfidenceAnalysis(
                confidence=0.5,
                ambiguities=existing_ambiguities + ["AI analysis unavailable"],
                reasoning=f"Heuristic fallback: {e}",
            )

    def _generate_reasoning(
        self,
        has_action_verb: bool,
        has_vague_pattern: bool,
        ambiguity_count: int,
    ) -> str:
        """Generate human-readable reasoning for the score."""
        reasons = []

        if has_action_verb:
            reasons.append("Clear action verb detected")
        else:
            reasons.append("No clear action verb")

        if has_vague_pattern:
            reasons.append("Contains vague language")

        if ambiguity_count == 0:
            reasons.append("No ambiguities found")
        else:
            reasons.append(f"{ambiguity_count} potential ambiguities")

        return "; ".join(reasons)


def get_confidence_service() -> ConfidenceService:
    """Factory function to get confidence scoring service.

    Returns:
        ConfidenceService instance.
    """
    return ConfidenceService()
