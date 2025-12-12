"""Task breakdown service (AGT-012).

Breaks down complex tasks into micro-steps that are physical, immediate, and tiny.
"""

from pydantic import BaseModel, Field
import structlog

from app.ai import AIProvider, get_ai_provider
from app.prompts.registry import get_prompt

logger = structlog.get_logger()


class BreakdownStep(BaseModel):
    """A single micro-step in a task breakdown."""

    title: str = Field(
        ...,
        max_length=100,
        description="Short, actionable step description",
    )
    estimated_minutes: int = Field(
        default=5,
        ge=1,
        le=15,
        description="Estimated time for this step (max 15 min)",
    )
    is_physical: bool = Field(
        default=True,
        description="Whether this step involves physical action",
    )


class BreakdownResult(BaseModel):
    """Result of breaking down a complex task."""

    steps: list[BreakdownStep] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="3-5 micro-steps for the task",
    )
    first_step_emphasis: str = Field(
        default="",
        description="Why the first step is key to getting started",
    )
    total_estimated_minutes: int = Field(
        default=0,
        description="Sum of all step estimates",
    )


class BreakdownService:
    """Service for breaking down overwhelming tasks.

    Generates 3-5 micro-steps that are:
    - PHYSICAL: involve body movement, not just thinking
    - IMMEDIATE: can start right now
    - TINY: each takes 2-10 minutes max

    Focus is on initiation - overcoming the paralysis of starting.
    """

    def __init__(self, ai_provider: AIProvider | None = None):
        """Initialize the breakdown service.

        Args:
            ai_provider: AI provider for completions. Defaults to configured provider.
        """
        self.ai = ai_provider or get_ai_provider()

    async def breakdown(self, task_title: str) -> BreakdownResult:
        """Break down a complex task into micro-steps.

        Args:
            task_title: The task to break down.

        Returns:
            BreakdownResult with 3-5 physical, immediate, tiny steps.
        """
        prompt = get_prompt("breakdown")
        logger.debug(
            "Breaking down task",
            task_title=task_title,
            prompt_version=prompt.version,
        )

        try:
            result = await self.ai.extract(
                text=f"Break down: {task_title}",
                schema=BreakdownResult,
                system=prompt.content,
            )

            # Calculate total estimated time
            result.total_estimated_minutes = sum(
                step.estimated_minutes for step in result.steps
            )

            logger.info(
                "Task broken down",
                task_title=task_title,
                step_count=len(result.steps),
                total_minutes=result.total_estimated_minutes,
            )

            return result
        except ValueError as e:
            logger.error("Breakdown failed", error=str(e), task_title=task_title)
            # Return minimal fallback breakdown
            return BreakdownResult(
                steps=[
                    BreakdownStep(
                        title=f"Open/prepare for: {task_title[:50]}",
                        estimated_minutes=2,
                        is_physical=True,
                    ),
                    BreakdownStep(
                        title="Do the first small part",
                        estimated_minutes=5,
                        is_physical=True,
                    ),
                    BreakdownStep(
                        title="Review what you did",
                        estimated_minutes=2,
                        is_physical=True,
                    ),
                ],
                first_step_emphasis="Just starting is the hardest part - focus only on step 1",
                total_estimated_minutes=9,
            )


def get_breakdown_service() -> BreakdownService:
    """Factory function to get breakdown service.

    Returns:
        BreakdownService instance.
    """
    return BreakdownService()
