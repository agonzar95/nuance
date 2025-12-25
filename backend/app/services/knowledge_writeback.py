"""Knowledge Writeback Service (MEM-001).

Extracts and persists knowledge objects from AgentOutputContract after each agent turn.
This is the bridge between the agent output pipeline and the knowledge object store.
"""

from datetime import datetime, UTC
from typing import Any

import structlog

from app.contracts.agent_output_v0 import (
    AgentOutputContract,
    Capture,
    AtomicTask,
    PsychologicalInsight,
    CognitiveLoadLevel,
)
from app.services.knowledge_objects import (
    KnowledgeObjectService,
    KnowledgeObjectCreate,
    KnowledgeObjectType,
    get_knowledge_object_service,
)

logger = structlog.get_logger()


class KnowledgeWritebackService:
    """Service that writes knowledge objects after each agent turn.

    Extracts structured knowledge from AgentOutputContract and persists:
    - Taxonomy labels for each capture
    - Breakdown structures (atomic task trees)
    - Psychological insights
    - State snapshots

    All operations are idempotent via natural_key constraints.
    """

    def __init__(
        self,
        knowledge_service: KnowledgeObjectService | None = None,
    ) -> None:
        """Initialize the writeback service.

        Args:
            knowledge_service: Knowledge object service (uses default if not provided).
        """
        self.knowledge = knowledge_service or get_knowledge_object_service()

    async def process_agent_output(
        self,
        user_id: str,
        contract: AgentOutputContract,
        source_message_id: str | None = None,
        source_conversation_id: str | None = None,
    ) -> WritebackResult:
        """Process an agent output and persist knowledge objects.

        This is the main entry point called after each agent turn.

        Args:
            user_id: The user's ID.
            contract: The AgentOutputContract from the agent turn.
            source_message_id: Optional message ID for linking.
            source_conversation_id: Optional conversation ID for linking.

        Returns:
            WritebackResult with counts and any errors.
        """
        result = WritebackResult()

        # Common provenance info
        provenance = {
            "model_id": contract.provenance.model_id if contract.provenance else None,
            "prompt_version": None,
            "request_id": contract.request_id,
        }
        if contract.provenance and contract.provenance.prompt_versions:
            # Get first prompt version as primary
            prompt_versions = list(contract.provenance.prompt_versions.values())
            if prompt_versions:
                provenance["prompt_version"] = prompt_versions[0]

        # Process captures and their taxonomy labels
        for capture in contract.output.captures:
            try:
                # Write taxonomy label
                if capture.labels:
                    label_obj = self._create_taxonomy_label(
                        capture=capture,
                        source_message_id=source_message_id,
                        source_conversation_id=source_conversation_id,
                        provenance=provenance,
                    )
                    ko = await self.knowledge.upsert(user_id, label_obj)
                    if ko:
                        result.taxonomy_labels_written += 1

                # Write magnitude/state as state_snapshot if significant
                if capture.magnitude or capture.state:
                    snapshot_obj = self._create_state_snapshot(
                        capture=capture,
                        source_message_id=source_message_id,
                        source_conversation_id=source_conversation_id,
                        provenance=provenance,
                    )
                    ko = await self.knowledge.upsert(user_id, snapshot_obj)
                    if ko:
                        result.state_snapshots_written += 1

            except Exception as e:
                logger.error(
                    "Failed to write knowledge for capture",
                    capture_id=capture.id,
                    error=str(e),
                )
                result.errors.append(f"capture:{capture.id}:{str(e)}")

        # Process atomic tasks (breakdowns)
        if contract.output.atomic_tasks:
            try:
                breakdown_obj = self._create_breakdown(
                    tasks=contract.output.atomic_tasks,
                    source_message_id=source_message_id,
                    source_conversation_id=source_conversation_id,
                    provenance=provenance,
                )
                ko = await self.knowledge.upsert(user_id, breakdown_obj)
                if ko:
                    result.breakdowns_written += 1
            except Exception as e:
                logger.error("Failed to write breakdown", error=str(e))
                result.errors.append(f"breakdown:{str(e)}")

        # Process insights
        for insight in contract.output.insights:
            try:
                insight_obj = self._create_insight(
                    insight=insight,
                    source_message_id=source_message_id,
                    source_conversation_id=source_conversation_id,
                    provenance=provenance,
                )
                ko = await self.knowledge.upsert(user_id, insight_obj)
                if ko:
                    result.insights_written += 1
            except Exception as e:
                logger.error(
                    "Failed to write insight",
                    pattern=insight.pattern_name,
                    error=str(e),
                )
                result.errors.append(f"insight:{insight.pattern_name}:{str(e)}")

        # Log coaching notes if coaching was involved
        if contract.output.coaching_message:
            try:
                coaching_obj = self._create_coaching_note(
                    message=contract.output.coaching_message,
                    cognitive_load=contract.output.cognitive_load,
                    source_message_id=source_message_id,
                    source_conversation_id=source_conversation_id,
                    provenance=provenance,
                )
                ko = await self.knowledge.upsert(user_id, coaching_obj)
                if ko:
                    result.coaching_notes_written += 1
            except Exception as e:
                logger.error("Failed to write coaching note", error=str(e))
                result.errors.append(f"coaching:{str(e)}")

        logger.info(
            "Knowledge writeback complete",
            user_id=user_id,
            request_id=contract.request_id,
            taxonomy_labels=result.taxonomy_labels_written,
            breakdowns=result.breakdowns_written,
            insights=result.insights_written,
            state_snapshots=result.state_snapshots_written,
            coaching_notes=result.coaching_notes_written,
            errors=len(result.errors),
        )

        return result

    def _create_taxonomy_label(
        self,
        capture: Capture,
        source_message_id: str | None,
        source_conversation_id: str | None,
        provenance: dict[str, Any],
    ) -> KnowledgeObjectCreate:
        """Create a taxonomy label knowledge object."""
        labels = capture.labels

        payload = {
            "capture_id": capture.id,
            "capture_title": capture.title,
            "intent_layer": labels.intent_layer.value if labels else None,
            "survival_function": labels.survival_function.value if labels else None,
            "cognitive_load": labels.cognitive_load.value if labels else None,
            "time_horizon": labels.time_horizon.value if labels else None,
            "agency_level": labels.agency_level.value if labels else None,
            "psych_source": labels.psych_source.value if labels else None,
            "system_role": labels.system_role.value if labels else None,
        }

        # Natural key based on capture ID ensures one label per capture
        natural_key = f"taxonomy:{capture.id}"

        return KnowledgeObjectCreate(
            type=KnowledgeObjectType.TAXONOMY_LABEL,
            payload=payload,
            confidence=capture.confidence,
            importance=self._calculate_importance(capture),
            source_message_id=source_message_id,
            source_conversation_id=source_conversation_id,
            natural_key=natural_key,
            model_id=provenance.get("model_id"),
            prompt_version=provenance.get("prompt_version"),
            request_id=provenance.get("request_id"),
        )

    def _create_state_snapshot(
        self,
        capture: Capture,
        source_message_id: str | None,
        source_conversation_id: str | None,
        provenance: dict[str, Any],
    ) -> KnowledgeObjectCreate:
        """Create a state snapshot knowledge object."""
        payload = {
            "capture_id": capture.id,
            "capture_title": capture.title,
            "capture_type": capture.type.value,
            "magnitude": {
                "scope": capture.magnitude.scope.value if capture.magnitude else None,
                "complexity": capture.magnitude.complexity if capture.magnitude else None,
                "dependencies": capture.magnitude.dependencies if capture.magnitude else 0,
                "uncertainty": capture.magnitude.uncertainty if capture.magnitude else 0,
            } if capture.magnitude else None,
            "state": {
                "stage": capture.state.stage.value if capture.state else None,
                "bottleneck": capture.state.bottleneck if capture.state else None,
                "energy_required": capture.state.energy_required.value if capture.state else None,
            } if capture.state else None,
            "avoidance_weight": capture.avoidance_weight,
            "estimated_minutes": capture.estimated_minutes,
            "needs_breakdown": capture.needs_breakdown,
            "ambiguities": capture.ambiguities,
        }

        # Natural key with timestamp to allow multiple snapshots over time
        natural_key = f"snapshot:{capture.id}:{provenance.get('request_id', 'unknown')}"

        return KnowledgeObjectCreate(
            type=KnowledgeObjectType.STATE_SNAPSHOT,
            payload=payload,
            confidence=capture.confidence,
            importance=self._calculate_importance(capture),
            source_message_id=source_message_id,
            source_conversation_id=source_conversation_id,
            natural_key=natural_key,
            model_id=provenance.get("model_id"),
            prompt_version=provenance.get("prompt_version"),
            request_id=provenance.get("request_id"),
        )

    def _create_breakdown(
        self,
        tasks: list[AtomicTask],
        source_message_id: str | None,
        source_conversation_id: str | None,
        provenance: dict[str, Any],
    ) -> KnowledgeObjectCreate:
        """Create a breakdown knowledge object."""
        # Group by parent capture
        parent_id = tasks[0].parent_capture_id if tasks else None

        steps = [
            {
                "id": task.id,
                "verb": task.verb,
                "object": task.object,
                "full_description": task.full_description,
                "definition_of_done": task.definition_of_done,
                "estimated_minutes": task.estimated_minutes,
                "energy_level": task.energy_level.value,
                "prerequisites": task.prerequisites,
                "is_first_action": task.is_first_action,
                "is_physical": task.is_physical,
            }
            for task in tasks
        ]

        total_minutes = sum(task.estimated_minutes for task in tasks)

        payload = {
            "parent_capture_id": parent_id,
            "steps": steps,
            "total_estimated_minutes": total_minutes,
            "step_count": len(steps),
            "first_action_id": next((t.id for t in tasks if t.is_first_action), None),
        }

        # Natural key based on parent capture
        natural_key = f"breakdown:{parent_id or 'orphan'}:{provenance.get('request_id', 'unknown')}"

        return KnowledgeObjectCreate(
            type=KnowledgeObjectType.BREAKDOWN,
            payload=payload,
            confidence=0.8,  # Breakdowns are generally reliable
            importance=70,  # Breakdowns are important for execution
            source_message_id=source_message_id,
            source_conversation_id=source_conversation_id,
            natural_key=natural_key,
            model_id=provenance.get("model_id"),
            prompt_version=provenance.get("prompt_version"),
            request_id=provenance.get("request_id"),
        )

    def _create_insight(
        self,
        insight: PsychologicalInsight,
        source_message_id: str | None,
        source_conversation_id: str | None,
        provenance: dict[str, Any],
    ) -> KnowledgeObjectCreate:
        """Create an insight knowledge object."""
        payload = {
            "pattern_name": insight.pattern_name,
            "description": insight.description,
            "suggested_strategy": insight.suggested_strategy,
        }

        # Natural key allows same pattern to be recorded per conversation
        natural_key = f"insight:{insight.pattern_name}:{source_conversation_id or 'none'}:{provenance.get('request_id', 'unknown')}"

        return KnowledgeObjectCreate(
            type=KnowledgeObjectType.INSIGHT,
            payload=payload,
            confidence=insight.confidence,
            importance=75,  # Insights are valuable for understanding user patterns
            source_message_id=source_message_id,
            source_conversation_id=source_conversation_id,
            natural_key=natural_key,
            model_id=provenance.get("model_id"),
            prompt_version=provenance.get("prompt_version"),
            request_id=provenance.get("request_id"),
        )

    def _create_coaching_note(
        self,
        message: str,
        cognitive_load: CognitiveLoadLevel,
        source_message_id: str | None,
        source_conversation_id: str | None,
        provenance: dict[str, Any],
    ) -> KnowledgeObjectCreate:
        """Create a coaching note knowledge object."""
        payload = {
            "message_summary": message[:500] if len(message) > 500 else message,
            "full_message_length": len(message),
            "cognitive_load": cognitive_load.value,
            "was_high_friction": cognitive_load == CognitiveLoadLevel.HIGH_FRICTION,
        }

        # Natural key per request
        natural_key = f"coaching:{provenance.get('request_id', 'unknown')}"

        return KnowledgeObjectCreate(
            type=KnowledgeObjectType.COACHING_NOTE,
            payload=payload,
            confidence=0.9,  # Coaching messages are directly observed
            importance=60,  # Useful for tracking emotional support needs
            source_message_id=source_message_id,
            source_conversation_id=source_conversation_id,
            natural_key=natural_key,
            model_id=provenance.get("model_id"),
            prompt_version=provenance.get("prompt_version"),
            request_id=provenance.get("request_id"),
        )

    def _calculate_importance(self, capture: Capture) -> int:
        """Calculate importance score for a capture.

        Higher avoidance and lower confidence = more important to track.

        Args:
            capture: The capture to score.

        Returns:
            Importance score 0-100.
        """
        base = 50

        # High avoidance items are more important to track
        avoidance_boost = (capture.avoidance_weight - 1) * 10  # 0-40

        # Lower confidence items need more attention
        confidence_boost = int((1 - capture.confidence) * 20)  # 0-20

        # Needs breakdown = more complex = more important
        breakdown_boost = 10 if capture.needs_breakdown else 0

        return min(100, base + avoidance_boost + confidence_boost + breakdown_boost)


class WritebackResult:
    """Result from a writeback operation."""

    def __init__(self) -> None:
        """Initialize result counters."""
        self.taxonomy_labels_written: int = 0
        self.breakdowns_written: int = 0
        self.insights_written: int = 0
        self.state_snapshots_written: int = 0
        self.coaching_notes_written: int = 0
        self.errors: list[str] = []

    @property
    def total_written(self) -> int:
        """Total objects written."""
        return (
            self.taxonomy_labels_written
            + self.breakdowns_written
            + self.insights_written
            + self.state_snapshots_written
            + self.coaching_notes_written
        )

    @property
    def success(self) -> bool:
        """Whether the writeback was successful (no errors)."""
        return len(self.errors) == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/response."""
        return {
            "total_written": self.total_written,
            "taxonomy_labels": self.taxonomy_labels_written,
            "breakdowns": self.breakdowns_written,
            "insights": self.insights_written,
            "state_snapshots": self.state_snapshots_written,
            "coaching_notes": self.coaching_notes_written,
            "errors": self.errors,
            "success": self.success,
        }


# =============================================================================
# Factory Function
# =============================================================================


_service: KnowledgeWritebackService | None = None


def get_knowledge_writeback_service() -> KnowledgeWritebackService:
    """Get or create the knowledge writeback service singleton."""
    global _service
    if _service is None:
        _service = KnowledgeWritebackService()
    return _service
