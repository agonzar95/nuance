"""Contract mapper for converting existing structures to AgentOutputContract v0.

This module provides mapping functions to convert existing response structures
(RouterResponse, OrchestrationResult, etc.) to the new AgentOutputContract format.
"""

import time
from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

import structlog

from app.contracts.agent_output_v0 import (
    AgentOutputContract,
    AgentOutput,
    Capture,
    AtomicTask,
    StateUpdate,
    ClarificationQuestion,
    UIBlock,
    PsychologicalInsight as ContractInsight,
    CommandResult,
    IntentClassification,
    Provenance,
    TokenUsage,
    # Enums
    IntentType,
    CaptureType,
    CognitiveLoadLevel,
    Scope,
    EnergyLevel,
    EntityType,
    Operation,
    QuestionType,
    UIBlockType,
    TaxonomyLayer,
    MagnitudeInference,
    StateInference,
    Stage,
    IntentLayer,
    SurvivalFunction,
    AgencyLevel,
    PsychSource,
    SystemRole,
    CONTRACT_VERSION,
)
from app.services.intent import Intent
from app.services.intent_router import RouterResponse, CommandResponse
from app.services.extraction_orchestrator import OrchestrationResult, EnrichedAction
from app.services.insight import InsightResult, PsychologicalInsight
from app.models.database import ActionComplexity

logger = structlog.get_logger()


def map_complexity_to_scope(complexity: ActionComplexity) -> Scope:
    """Map ActionComplexity enum to Scope enum."""
    mapping = {
        ActionComplexity.ATOMIC: Scope.ATOMIC,
        ActionComplexity.COMPOSITE: Scope.COMPOSITE,
        ActionComplexity.PROJECT: Scope.PROJECT,
    }
    return mapping.get(complexity, Scope.ATOMIC)


def map_cognitive_load(load: str) -> CognitiveLoadLevel:
    """Map cognitive load string to enum."""
    if load.upper() == "HIGH_FRICTION":
        return CognitiveLoadLevel.HIGH_FRICTION
    return CognitiveLoadLevel.ROUTINE


def map_intent_to_type(intent: Intent) -> IntentType:
    """Map Intent enum to IntentType enum."""
    mapping = {
        Intent.CAPTURE: IntentType.CAPTURE,
        Intent.COACHING: IntentType.COACHING,
        Intent.COMMAND: IntentType.COMMAND,
        Intent.CLARIFY: IntentType.CLARIFY,
    }
    return mapping.get(intent, IntentType.CAPTURE)


def infer_taxonomy_from_action(action: EnrichedAction) -> TaxonomyLayer:
    """Infer taxonomy labels from an enriched action."""
    # Infer cognitive load
    cognitive_load = CognitiveLoadLevel.HIGH_FRICTION if action.cognitive_load == "HIGH_FRICTION" else CognitiveLoadLevel.ROUTINE

    # Infer system role based on avoidance and complexity
    if action.avoidance_weight >= 4 or action.complexity == ActionComplexity.PROJECT:
        system_role = SystemRole.SCAFFOLD
    elif action.needs_breakdown:
        system_role = SystemRole.SCAFFOLD
    else:
        system_role = SystemRole.TRACK

    # Infer psych source from avoidance
    if action.avoidance_weight >= 3:
        psych_source = PsychSource.AVOIDANCE
    else:
        psych_source = PsychSource.INTRINSIC

    return TaxonomyLayer(
        intent_layer=IntentLayer.EXECUTE,
        survival_function=SurvivalFunction.UNKNOWN,  # Would need more context
        cognitive_load=cognitive_load,
        time_horizon=TimeHorizon.UNKNOWN,  # Would need more context
        agency_level=AgencyLevel.AUTONOMOUS,
        psych_source=psych_source,
        system_role=system_role,
    )


def infer_magnitude_from_action(action: EnrichedAction) -> MagnitudeInference:
    """Infer magnitude from an enriched action."""
    # Map complexity to a 1-5 scale
    complexity_score = {
        ActionComplexity.ATOMIC: 1,
        ActionComplexity.COMPOSITE: 3,
        ActionComplexity.PROJECT: 5,
    }.get(action.complexity, 2)

    return MagnitudeInference(
        scope=map_complexity_to_scope(action.complexity),
        complexity=complexity_score,
        dependencies=0,  # Not tracked in current system
        uncertainty=1.0 - action.confidence,
    )


def infer_state_from_action(action: EnrichedAction) -> StateInference:
    """Infer state from an enriched action."""
    # Determine energy level from avoidance
    if action.avoidance_weight >= 4:
        energy = EnergyLevel.HIGH
    elif action.avoidance_weight >= 2:
        energy = EnergyLevel.MEDIUM
    else:
        energy = EnergyLevel.LOW

    # Bottleneck from ambiguities
    bottleneck = None
    if action.ambiguities:
        bottleneck = f"Needs clarification: {', '.join(action.ambiguities[:2])}"
    elif action.avoidance_weight >= 4:
        bottleneck = "Emotional resistance detected"

    return StateInference(
        stage=Stage.NOT_STARTED,
        bottleneck=bottleneck,
        energy_required=energy,
    )


def map_enriched_action_to_capture(
    action: EnrichedAction,
    capture_id: str | None = None,
) -> Capture:
    """Convert an EnrichedAction to a Capture."""
    cap_id = capture_id or f"cap_{uuid4().hex[:8]}"

    return Capture(
        id=cap_id,
        type=CaptureType.TASK,
        title=action.title,
        raw_segment=action.raw_segment,
        estimated_minutes=action.estimated_minutes,
        avoidance_weight=action.avoidance_weight,
        confidence=action.confidence,
        ambiguities=action.ambiguities,
        labels=infer_taxonomy_from_action(action),
        magnitude=infer_magnitude_from_action(action),
        state=infer_state_from_action(action),
        needs_breakdown=action.needs_breakdown,
    )


def map_insight_to_contract(insight: PsychologicalInsight) -> ContractInsight:
    """Convert a PsychologicalInsight to contract format."""
    return ContractInsight(
        pattern_name=insight.pattern_name,
        description=insight.description,
        suggested_strategy=insight.suggested_strategy,
        confidence=insight.confidence,
    )


def create_state_update_for_capture(capture: Capture) -> StateUpdate:
    """Create a state update for a new capture."""
    return StateUpdate(
        entity_type=EntityType.ACTION,
        entity_id=None,  # Will be set on persistence
        temp_id=capture.id,
        operation=Operation.CREATED,
        changes={
            "title": capture.title,
            "status": "inbox",
            "complexity": capture.magnitude.scope.value if capture.magnitude else "atomic",
            "avoidance_weight": capture.avoidance_weight,
            "estimated_minutes": capture.estimated_minutes,
        },
    )


def create_ui_blocks_for_captures(
    captures: list[Capture],
    needs_scaffolding: bool,
    scaffolding_question: str | None,
) -> list[UIBlock]:
    """Create UI blocks for capture results."""
    blocks: list[UIBlock] = []

    # Main capture list
    high_friction = [c.id for c in captures if c.avoidance_weight >= 4]
    blocks.append(UIBlock(
        type=UIBlockType.CAPTURE_LIST,
        data={
            "captures": [c.id for c in captures],
            "highlight_high_friction": high_friction,
        },
        priority=0,
    ))

    # Scaffolding question if needed
    if needs_scaffolding and scaffolding_question:
        blocks.append(UIBlock(
            type=UIBlockType.QUESTION_PROMPT,
            data={
                "scaffolding_question": scaffolding_question,
                "style": "prominent",
            },
            priority=1,
        ))

    return blocks


def create_ui_blocks_for_coaching(coaching_message: str) -> list[UIBlock]:
    """Create UI blocks for coaching response."""
    return [
        UIBlock(
            type=UIBlockType.COACHING_MESSAGE,
            data={
                "message": coaching_message,
                "tone": "warm_supportive",
            },
            priority=0,
        )
    ]


def create_ui_blocks_for_command(command_result: CommandResponse) -> list[UIBlock]:
    """Create UI blocks for command response."""
    return [
        UIBlock(
            type=UIBlockType.COMMAND_RESULT,
            data={
                "command": command_result.command,
                "message": command_result.message,
                "data": command_result.data,
            },
            priority=0,
        )
    ]


def generate_user_facing_summary(
    intent: Intent,
    captures: list[Capture],
    coaching_message: str | None,
    command_result: CommandResponse | None,
) -> str:
    """Generate a human-readable summary of the agent turn."""
    if intent == Intent.CAPTURE:
        count = len(captures)
        if count == 0:
            return "I couldn't find any specific tasks to capture. Could you tell me more about what you'd like to do?"
        elif count == 1:
            return f"Got it! I captured 1 task: '{captures[0].title}'."
        else:
            high_friction = [c for c in captures if c.avoidance_weight >= 4]
            if high_friction:
                return f"Got it! I captured {count} tasks. Some seem to be weighing on you - I can help break those down if you'd like."
            return f"Got it! I captured {count} tasks for you."

    elif intent == Intent.COACHING:
        return "I'm here to help. Let's work through this together."

    elif intent == Intent.COMMAND:
        if command_result:
            return command_result.message
        return "Command processed."

    elif intent == Intent.CLARIFY:
        return "I captured some items but need a bit more detail to make sure I got them right."

    return "Response processed."


def map_router_response_to_contract(
    response: RouterResponse,
    raw_input: str,
    request_id: str | None = None,
    trace_id: str | None = None,
    processing_time_ms: int = 0,
    prompt_versions: dict[str, str] | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> AgentOutputContract:
    """Convert a RouterResponse to AgentOutputContract.

    This is the main mapping function that bridges the existing system
    with the new contract format.

    Args:
        response: The existing RouterResponse from intent_router.
        raw_input: Original user input text.
        request_id: Optional request ID (generated if not provided).
        trace_id: Optional trace ID for distributed tracing.
        processing_time_ms: Time taken to process the request.
        prompt_versions: Map of prompt names to versions used.
        input_tokens: Input tokens consumed.
        output_tokens: Output tokens generated.

    Returns:
        AgentOutputContract with mapped data.
    """
    req_id = request_id or str(uuid4())

    # Map captures from extraction result
    captures: list[Capture] = []
    if response.extraction and response.extraction.actions:
        for i, action in enumerate(response.extraction.actions):
            capture = map_enriched_action_to_capture(action)
            captures.append(capture)

    # Create state updates for new captures
    state_updates = [create_state_update_for_capture(c) for c in captures]

    # Map insights
    insights: list[ContractInsight] = []
    if response.insight:
        # response.insight could be InsightResult or PsychologicalInsight
        if hasattr(response.insight, "insights"):
            for insight in response.insight.insights:
                insights.append(map_insight_to_contract(insight))
        elif hasattr(response.insight, "pattern_name"):
            insights.append(map_insight_to_contract(response.insight))

    # Map command result
    command_result: CommandResult | None = None
    if response.command_response:
        command_result = CommandResult(
            command=response.command_response.command,
            message=response.command_response.message,
            data=response.command_response.data,
        )

    # Determine cognitive load
    cognitive_load = CognitiveLoadLevel.ROUTINE
    if response.extraction:
        cognitive_load = map_cognitive_load(response.extraction.cognitive_load)

    # Determine needs_scaffolding and question
    needs_scaffolding = False
    scaffolding_question: str | None = None
    if response.extraction:
        needs_scaffolding = response.extraction.needs_scaffolding
        scaffolding_question = response.extraction.scaffolding_question

    # Create clarification questions if low confidence
    questions: list[ClarificationQuestion] = []
    if response.extraction and response.extraction.overall_confidence < 0.7:
        for capture in captures:
            if capture.ambiguities:
                for i, amb in enumerate(capture.ambiguities[:2]):  # Max 2 per capture
                    questions.append(ClarificationQuestion(
                        id=f"q_{capture.id}_{i}",
                        question=amb,
                        target_capture_id=capture.id,
                        question_type=QuestionType.SCOPE,
                        suggested_answers=[],
                    ))

    # Create UI blocks based on intent
    ui_blocks: list[UIBlock] = []
    if response.intent == Intent.CAPTURE or response.intent == Intent.CLARIFY:
        ui_blocks = create_ui_blocks_for_captures(captures, needs_scaffolding, scaffolding_question)
        if insights:
            ui_blocks.append(UIBlock(
                type=UIBlockType.INSIGHT_CARD,
                data={"insights": [i.pattern_name for i in insights]},
                priority=len(ui_blocks),
            ))
    elif response.intent == Intent.COACHING and response.coaching_response:
        ui_blocks = create_ui_blocks_for_coaching(response.coaching_response)
    elif response.intent == Intent.COMMAND and response.command_response:
        ui_blocks = create_ui_blocks_for_command(response.command_response)

    # Generate summary
    user_facing_summary = generate_user_facing_summary(
        response.intent,
        captures,
        response.coaching_response,
        response.command_response,
    )

    # Determine overall confidence
    overall_confidence = response.intent_confidence
    if response.extraction:
        overall_confidence = min(response.intent_confidence, response.extraction.overall_confidence)

    # Build output
    output = AgentOutput(
        raw_input=raw_input,
        captures=captures,
        atomic_tasks=[],  # Generated on-demand via breakdown service
        state_updates=state_updates,
        questions=questions,
        insights=insights,
        coaching_message=response.coaching_response,
        command_result=command_result,
        user_facing_summary=user_facing_summary,
        ui_blocks=ui_blocks,
        overall_confidence=overall_confidence,
        cognitive_load=cognitive_load,
        needs_scaffolding=needs_scaffolding,
        scaffolding_question=scaffolding_question,
    )

    # Build provenance
    provenance = Provenance(
        model_id="claude-3-5-sonnet-20241022",  # Could be passed in
        prompt_versions=prompt_versions or {},
        processing_time_ms=processing_time_ms,
        token_usage=TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        ) if input_tokens or output_tokens else None,
    )

    # Build contract
    return AgentOutputContract(
        contract_version=CONTRACT_VERSION,
        request_id=req_id,
        trace_id=trace_id,
        timestamp=datetime.now(UTC),
        intent=IntentClassification(
            type=map_intent_to_type(response.intent),
            confidence=response.intent_confidence,
            reasoning=None,
        ),
        output=output,
        provenance=provenance,
    )


# Import TimeHorizon that was missing
from app.contracts.agent_output_v0 import TimeHorizon


class ContractMapper:
    """Service class for mapping responses to contracts.

    Provides a stateful mapper that can track prompt versions and
    accumulate token usage across a request.
    """

    def __init__(self) -> None:
        """Initialize the mapper."""
        self._start_time: float | None = None
        self._prompt_versions: dict[str, str] = {}
        self._input_tokens: int = 0
        self._output_tokens: int = 0

    def start_timing(self) -> None:
        """Start timing the request."""
        self._start_time = time.time()

    def record_prompt_version(self, name: str, version: str) -> None:
        """Record a prompt version used."""
        self._prompt_versions[name] = version

    def record_tokens(self, input_tokens: int, output_tokens: int) -> None:
        """Accumulate token usage."""
        self._input_tokens += input_tokens
        self._output_tokens += output_tokens

    def get_processing_time_ms(self) -> int:
        """Get elapsed time in milliseconds."""
        if self._start_time is None:
            return 0
        return int((time.time() - self._start_time) * 1000)

    def map_response(
        self,
        response: RouterResponse,
        raw_input: str,
        request_id: str | None = None,
        trace_id: str | None = None,
    ) -> AgentOutputContract:
        """Map a RouterResponse to AgentOutputContract with accumulated metadata."""
        return map_router_response_to_contract(
            response=response,
            raw_input=raw_input,
            request_id=request_id,
            trace_id=trace_id,
            processing_time_ms=self.get_processing_time_ms(),
            prompt_versions=self._prompt_versions,
            input_tokens=self._input_tokens,
            output_tokens=self._output_tokens,
        )

    def reset(self) -> None:
        """Reset the mapper state."""
        self._start_time = None
        self._prompt_versions = {}
        self._input_tokens = 0
        self._output_tokens = 0


def get_contract_mapper() -> ContractMapper:
    """Factory function for contract mapper."""
    return ContractMapper()
