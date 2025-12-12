"""Avoidance weight extraction service (AGT-009).

Detects emotional resistance in task descriptions and scores from 1-5.
"""

from pydantic import BaseModel, Field
import structlog

from app.ai import AIProvider, get_ai_provider
from app.prompts.registry import get_prompt

logger = structlog.get_logger()


class AvoidanceAnalysis(BaseModel):
    """Result of avoidance weight analysis."""

    weight: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Avoidance weight from 1 (easy) to 5 (high resistance)",
    )
    signals: list[str] = Field(
        default_factory=list,
        description="Detected avoidance signals in the text",
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of the weight score",
    )


class AvoidanceService:
    """Service for detecting emotional resistance in tasks.

    Analyzes task descriptions for signals of avoidance, dread, or
    anxiety to help the system provide appropriate support.
    """

    def __init__(self, ai_provider: AIProvider | None = None):
        """Initialize the avoidance detection service.

        Args:
            ai_provider: AI provider for completions. Defaults to configured provider.
        """
        self.ai = ai_provider or get_ai_provider()

    async def detect(self, title: str, raw_input: str | None = None) -> AvoidanceAnalysis:
        """Detect avoidance weight for a task.

        Args:
            title: The action title.
            raw_input: Optional original user input for more context.

        Returns:
            AvoidanceAnalysis with weight 1-5 and detected signals.
        """
        # Use raw_input if available, otherwise just title
        text_to_analyze = f"Task: {title}"
        if raw_input:
            text_to_analyze += f"\nOriginal input: {raw_input}"

        prompt = get_prompt("avoidance")
        logger.debug(
            "Analyzing avoidance",
            title=title,
            prompt_version=prompt.version,
        )

        try:
            result = await self.ai.extract(
                text=text_to_analyze,
                schema=AvoidanceAnalysis,
                system=prompt.content,
            )

            logger.info(
                "Avoidance analyzed",
                title=title,
                weight=result.weight,
                signal_count=len(result.signals),
            )

            return result
        except ValueError as e:
            logger.error("Avoidance detection failed", error=str(e), title=title)
            # Default to weight 1 (neutral) on failure
            return AvoidanceAnalysis(
                weight=1,
                signals=[],
                reasoning=f"Analysis failed: {e}",
            )

    async def detect_batch(
        self, tasks: list[tuple[str, str | None]]
    ) -> list[AvoidanceAnalysis]:
        """Detect avoidance for multiple tasks.

        Args:
            tasks: List of (title, raw_input) tuples.

        Returns:
            List of AvoidanceAnalysis results in same order as input.
        """
        import asyncio

        results = await asyncio.gather(
            *[self.detect(title, raw_input) for title, raw_input in tasks],
            return_exceptions=True,
        )

        # Handle any exceptions that were gathered
        processed_results: list[AvoidanceAnalysis] = []
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                logger.error(
                    "Batch avoidance detection failed",
                    task_index=i,
                    error=str(result),
                )
                processed_results.append(
                    AvoidanceAnalysis(weight=1, signals=[], reasoning="Batch error")
                )
            else:
                processed_results.append(result)

        return processed_results


def get_avoidance_service() -> AvoidanceService:
    """Factory function to get avoidance detection service.

    Returns:
        AvoidanceService instance.
    """
    return AvoidanceService()
