"""Extraction orchestrator service (AGT-016).

Coordinates all extraction operations to produce complete, validated action data.
"""

import asyncio
from dataclasses import dataclass

from pydantic import BaseModel, Field
import structlog

from app.models.database import ActionComplexity
from app.services.extraction import (
    ExtractionService,
    ExtractionResult,
    ExtractedAction,
    get_extraction_service,
)
from app.services.avoidance import (
    AvoidanceService,
    AvoidanceAnalysis,
    get_avoidance_service,
)
from app.services.complexity import (
    ComplexityService,
    ComplexityAnalysis,
    get_complexity_service,
)
from app.services.confidence import (
    ConfidenceService,
    ConfidenceAnalysis,
    get_confidence_service,
)

logger = structlog.get_logger()


class EnrichedAction(BaseModel):
    """An action enriched with all extraction metadata."""

    title: str = Field(..., description="Action title")
    estimated_minutes: int = Field(default=15, description="Estimated time")
    raw_segment: str = Field(..., description="Original text segment")
    avoidance_weight: int = Field(default=1, ge=1, le=5, description="Avoidance score")
    complexity: ActionComplexity = Field(
        default=ActionComplexity.ATOMIC, description="Task complexity"
    )
    needs_breakdown: bool = Field(default=False, description="Should task be broken down")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Extraction confidence")
    ambiguities: list[str] = Field(default_factory=list, description="Potential clarifications")


class OrchestrationResult(BaseModel):
    """Result from the extraction orchestrator."""

    actions: list[EnrichedAction] = Field(
        default_factory=list, description="Enriched actions"
    )
    raw_input: str = Field(..., description="Original input text")
    overall_confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Overall extraction confidence"
    )
    needs_validation: bool = Field(
        default=False, description="Whether user validation is recommended"
    )


@dataclass
class ExtractionPipeline:
    """Dependencies for the extraction pipeline."""

    extraction: ExtractionService
    avoidance: AvoidanceService
    complexity: ComplexityService
    confidence: ConfidenceService


class ExtractionOrchestrator:
    """Orchestrates the full extraction pipeline.

    Pipeline:
    1. Extract actions from raw text (AGT-008)
    2. For each action, in parallel:
       - Analyze avoidance weight (AGT-009)
       - Classify complexity (AGT-010)
    3. Score confidence for each action (AGT-011)
    4. Return enriched actions with all metadata
    """

    def __init__(
        self,
        extraction_service: ExtractionService | None = None,
        avoidance_service: AvoidanceService | None = None,
        complexity_service: ComplexityService | None = None,
        confidence_service: ConfidenceService | None = None,
    ):
        """Initialize the orchestrator with all required services.

        Args:
            extraction_service: Action extraction service.
            avoidance_service: Avoidance detection service.
            complexity_service: Complexity classification service.
            confidence_service: Confidence scoring service.
        """
        self.extraction = extraction_service or get_extraction_service()
        self.avoidance = avoidance_service or get_avoidance_service()
        self.complexity = complexity_service or get_complexity_service()
        self.confidence = confidence_service or get_confidence_service()

    async def extract(self, text: str) -> OrchestrationResult:
        """Run the full extraction pipeline on input text.

        Args:
            text: Raw user input text.

        Returns:
            OrchestrationResult with enriched actions and metadata.
        """
        if not text or not text.strip():
            logger.warning("Empty input for extraction orchestration")
            return OrchestrationResult(
                actions=[],
                raw_input=text or "",
                overall_confidence=0.0,
                needs_validation=True,
            )

        logger.info("Starting extraction orchestration", input_length=len(text))

        # Step 1: Extract actions
        extraction_result = await self.extraction.extract(text)

        if not extraction_result.actions:
            logger.info("No actions extracted from input")
            return OrchestrationResult(
                actions=[],
                raw_input=text,
                overall_confidence=extraction_result.confidence,
                needs_validation=extraction_result.confidence < 0.7,
            )

        # Step 2: Enrich each action in parallel
        enriched_actions = await self._enrich_actions(
            extraction_result.actions, text
        )

        # Calculate overall confidence
        if enriched_actions:
            avg_confidence = sum(a.confidence for a in enriched_actions) / len(enriched_actions)
        else:
            avg_confidence = extraction_result.confidence

        needs_validation = avg_confidence < 0.7 or any(
            len(a.ambiguities) > 0 for a in enriched_actions
        )

        logger.info(
            "Extraction orchestration complete",
            action_count=len(enriched_actions),
            overall_confidence=avg_confidence,
            needs_validation=needs_validation,
        )

        return OrchestrationResult(
            actions=enriched_actions,
            raw_input=text,
            overall_confidence=round(avg_confidence, 2),
            needs_validation=needs_validation,
        )

    async def _enrich_actions(
        self,
        actions: list[ExtractedAction],
        raw_input: str,
    ) -> list[EnrichedAction]:
        """Enrich extracted actions with metadata.

        Args:
            actions: List of extracted actions.
            raw_input: Original input text.

        Returns:
            List of enriched actions.
        """
        enrichment_tasks = [
            self._enrich_single_action(action, raw_input)
            for action in actions
        ]

        results = await asyncio.gather(*enrichment_tasks, return_exceptions=True)

        enriched: list[EnrichedAction] = []
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                logger.error(
                    "Action enrichment failed",
                    action_index=i,
                    error=str(result),
                )
                # Create minimal enriched action on failure
                enriched.append(EnrichedAction(
                    title=actions[i].title,
                    estimated_minutes=actions[i].estimated_minutes,
                    raw_segment=actions[i].raw_segment,
                    avoidance_weight=1,
                    complexity=ActionComplexity.ATOMIC,
                    needs_breakdown=False,
                    confidence=0.5,
                    ambiguities=["Enrichment failed"],
                ))
            else:
                enriched.append(result)

        return enriched

    async def _enrich_single_action(
        self,
        action: ExtractedAction,
        raw_input: str,
    ) -> EnrichedAction:
        """Enrich a single action with all metadata.

        Args:
            action: The extracted action.
            raw_input: Original input text.

        Returns:
            Enriched action with avoidance, complexity, and confidence.
        """
        # Run avoidance and complexity analysis in parallel
        avoidance_task = self.avoidance.detect(action.title, action.raw_segment)
        complexity_task = self.complexity.classify(
            action.title, action.estimated_minutes
        )

        avoidance_result, complexity_result = await asyncio.gather(
            avoidance_task, complexity_task
        )

        # Score confidence (may use avoidance/complexity results)
        confidence_result = await self.confidence.score(action, raw_input)

        return EnrichedAction(
            title=action.title,
            estimated_minutes=action.estimated_minutes,
            raw_segment=action.raw_segment,
            avoidance_weight=avoidance_result.weight,
            complexity=complexity_result.complexity,
            needs_breakdown=complexity_result.needs_breakdown,
            confidence=confidence_result.confidence,
            ambiguities=confidence_result.ambiguities,
        )


def get_extraction_orchestrator() -> ExtractionOrchestrator:
    """Factory function to get extraction orchestrator.

    Returns:
        ExtractionOrchestrator instance.
    """
    return ExtractionOrchestrator()
