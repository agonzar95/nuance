"""Action extraction service (AGT-008).

Extracts structured actions from natural language input.
"""

from pydantic import BaseModel, Field
import structlog

from app.ai import AIProvider, get_ai_provider
from app.prompts.registry import get_prompt

logger = structlog.get_logger()


class ExtractedAction(BaseModel):
    """A single extracted action from user input."""

    title: str = Field(..., description="Clear, actionable task title", max_length=500)
    estimated_minutes: int = Field(
        default=15, ge=5, le=480, description="Estimated time in minutes"
    )
    raw_segment: str = Field(
        ..., description="Original text this action was extracted from"
    )


class ExtractionResult(BaseModel):
    """Result of action extraction from text."""

    actions: list[ExtractedAction] = Field(
        default_factory=list, description="List of extracted actions"
    )
    confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence in extraction"
    )
    ambiguities: list[str] = Field(
        default_factory=list, description="Ambiguities that may need clarification"
    )


class ExtractionService:
    """Service for extracting actions from natural language.

    Uses AI to parse user input and identify actionable tasks,
    estimating time and preserving the original language where possible.
    """

    def __init__(self, ai_provider: AIProvider | None = None):
        """Initialize the extraction service.

        Args:
            ai_provider: AI provider for completions. Defaults to configured provider.
        """
        self.ai = ai_provider or get_ai_provider()

    async def extract(self, text: str) -> ExtractionResult:
        """Extract actions from natural language text.

        Args:
            text: Raw user input text.

        Returns:
            ExtractionResult containing extracted actions and confidence.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for extraction")
            return ExtractionResult(
                actions=[], confidence=0.0, ambiguities=["No input provided"]
            )

        prompt = get_prompt("extraction")
        logger.debug(
            "Extracting actions",
            text_length=len(text),
            prompt_version=prompt.version,
        )

        try:
            result = await self.ai.extract(
                text=text,
                schema=ExtractionResult,
                system=prompt.content,
            )

            logger.info(
                "Actions extracted",
                action_count=len(result.actions),
                confidence=result.confidence,
            )

            return result
        except ValueError as e:
            logger.error("Action extraction failed", error=str(e), text=text[:100])
            # Return empty result on parsing failure
            return ExtractionResult(
                actions=[],
                confidence=0.0,
                ambiguities=[f"Failed to parse response: {e}"],
            )


def get_extraction_service() -> ExtractionService:
    """Factory function to get extraction service.

    Returns:
        ExtractionService instance.
    """
    return ExtractionService()
