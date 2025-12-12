"""Complexity classification service (AGT-010).

Classifies tasks as atomic, composite, or project based on complexity.
"""

from pydantic import BaseModel, Field
import structlog

from app.ai import AIProvider, get_ai_provider
from app.models.database import ActionComplexity
from app.prompts.registry import get_prompt

logger = structlog.get_logger()


class ComplexityAnalysis(BaseModel):
    """Result of complexity classification."""

    complexity: ActionComplexity = Field(
        default=ActionComplexity.ATOMIC,
        description="Complexity level: atomic, composite, or project",
    )
    suggested_steps: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Estimated number of sub-steps needed",
    )
    needs_breakdown: bool = Field(
        default=False,
        description="Whether the task should be broken down before execution",
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of the classification",
    )


class ComplexityService:
    """Service for classifying task complexity.

    Analyzes tasks to determine if they are simple (atomic), multi-step
    (composite), or require planning (project). Used to decide when to
    prompt for task breakdown.
    """

    def __init__(self, ai_provider: AIProvider | None = None):
        """Initialize the complexity classification service.

        Args:
            ai_provider: AI provider for completions. Defaults to configured provider.
        """
        self.ai = ai_provider or get_ai_provider()

    async def classify(
        self, title: str, estimated_minutes: int = 15
    ) -> ComplexityAnalysis:
        """Classify the complexity of a task.

        Args:
            title: The action title.
            estimated_minutes: Estimated time in minutes.

        Returns:
            ComplexityAnalysis with classification and breakdown recommendation.
        """
        # Fast path: short tasks are atomic
        if estimated_minutes <= 20:
            logger.debug(
                "Fast-path atomic classification",
                title=title,
                estimated_minutes=estimated_minutes,
            )
            return ComplexityAnalysis(
                complexity=ActionComplexity.ATOMIC,
                suggested_steps=1,
                needs_breakdown=False,
                reasoning=f"Short task ({estimated_minutes} min) - atomic by default",
            )

        # For longer tasks, use AI classification
        text_to_analyze = f"Task: {title} (estimated {estimated_minutes} minutes)"

        prompt = get_prompt("complexity")
        logger.debug(
            "Classifying complexity",
            title=title,
            estimated_minutes=estimated_minutes,
            prompt_version=prompt.version,
        )

        try:
            result = await self.ai.extract(
                text=text_to_analyze,
                schema=ComplexityAnalysis,
                system=prompt.content,
            )

            # Set needs_breakdown based on complexity
            if result.complexity != ActionComplexity.ATOMIC and not result.needs_breakdown:
                result.needs_breakdown = True

            logger.info(
                "Complexity classified",
                title=title,
                complexity=result.complexity.value,
                needs_breakdown=result.needs_breakdown,
            )

            return result
        except ValueError as e:
            logger.error("Complexity classification failed", error=str(e), title=title)
            # Default to composite for longer tasks on failure
            default_complexity = (
                ActionComplexity.COMPOSITE
                if estimated_minutes > 60
                else ActionComplexity.ATOMIC
            )
            return ComplexityAnalysis(
                complexity=default_complexity,
                suggested_steps=3 if estimated_minutes > 60 else 1,
                needs_breakdown=estimated_minutes > 60,
                reasoning=f"Classification failed, defaulting based on time: {e}",
            )


def get_complexity_service() -> ComplexityService:
    """Factory function to get complexity classification service.

    Returns:
        ComplexityService instance.
    """
    return ComplexityService()
