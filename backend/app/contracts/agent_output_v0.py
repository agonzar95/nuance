"""Agent Output Contract v0.

Standardized output contract for all agent turns, regardless of intent type.
This module defines the canonical response structure that every agent turn returns.

Contract Version: 0.1.0
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================


class IntentType(str, Enum):
    """Classified intent type."""

    CAPTURE = "capture"
    COACHING = "coaching"
    COMMAND = "command"
    CLARIFY = "clarify"


class CaptureType(str, Enum):
    """Type of captured item."""

    GOAL = "goal"
    PLAN = "plan"
    HABIT = "habit"
    TASK = "task"
    REFLECTION = "reflection"
    BLOCKER = "blocker"
    METRIC = "metric"


class IntentLayer(str, Enum):
    """What the user intends to do."""

    CAPTURE = "capture"
    CLARIFY = "clarify"
    EXECUTE = "execute"
    REFLECT = "reflect"
    UNKNOWN = "unknown"


class SurvivalFunction(str, Enum):
    """Core need being addressed."""

    MAINTENANCE = "maintenance"
    GROWTH = "growth"
    PROTECTION = "protection"
    CONNECTION = "connection"
    UNKNOWN = "unknown"


class CognitiveLoadLevel(str, Enum):
    """Mental effort required."""

    ROUTINE = "routine"
    HIGH_FRICTION = "high_friction"
    UNKNOWN = "unknown"


class TimeHorizon(str, Enum):
    """When this needs attention."""

    IMMEDIATE = "immediate"
    TODAY = "today"
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    LONG_TERM = "long_term"
    UNKNOWN = "unknown"


class AgencyLevel(str, Enum):
    """User's control over this item."""

    AUTONOMOUS = "autonomous"
    DELEGATED = "delegated"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class PsychSource(str, Enum):
    """Psychological motivation source."""

    INTRINSIC = "intrinsic"
    EXTRINSIC = "extrinsic"
    AVOIDANCE = "avoidance"
    UNKNOWN = "unknown"


class SystemRole(str, Enum):
    """What role the system should play."""

    CAPTURE = "capture"
    SCAFFOLD = "scaffold"
    TRACK = "track"
    REMIND = "remind"
    COACH = "coach"
    UNKNOWN = "unknown"


class Scope(str, Enum):
    """Size/scope of the item."""

    ATOMIC = "atomic"
    COMPOSITE = "composite"
    PROJECT = "project"


class Stage(str, Enum):
    """Current lifecycle stage."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    WAITING = "waiting"
    DONE = "done"
    UNKNOWN = "unknown"


class EnergyLevel(str, Enum):
    """Energy/effort required."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    """Type of database entity."""

    ACTION = "action"
    CONVERSATION = "conversation"
    MESSAGE = "message"
    PROFILE = "profile"


class Operation(str, Enum):
    """Type of entity change."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class QuestionType(str, Enum):
    """Category of clarification."""

    SCOPE = "scope"
    TIMELINE = "timeline"
    PRIORITY = "priority"
    BLOCKER = "blocker"
    OTHER = "other"


class UIBlockType(str, Enum):
    """Type of UI block."""

    CAPTURE_LIST = "capture_list"
    BREAKDOWN_STEPS = "breakdown_steps"
    COACHING_MESSAGE = "coaching_message"
    INSIGHT_CARD = "insight_card"
    QUESTION_PROMPT = "question_prompt"
    COMMAND_RESULT = "command_result"


# =============================================================================
# Taxonomy & Inference Models
# =============================================================================


class TaxonomyLayer(BaseModel):
    """7-layer taxonomy classification for a capture."""

    intent_layer: IntentLayer = Field(
        default=IntentLayer.UNKNOWN,
        description="What the user intends to do",
    )
    survival_function: SurvivalFunction = Field(
        default=SurvivalFunction.UNKNOWN,
        description="Core need being addressed",
    )
    cognitive_load: CognitiveLoadLevel = Field(
        default=CognitiveLoadLevel.UNKNOWN,
        description="Mental effort required",
    )
    time_horizon: TimeHorizon = Field(
        default=TimeHorizon.UNKNOWN,
        description="When this needs attention",
    )
    agency_level: AgencyLevel = Field(
        default=AgencyLevel.UNKNOWN,
        description="User's control over this item",
    )
    psych_source: PsychSource = Field(
        default=PsychSource.UNKNOWN,
        description="Psychological motivation source",
    )
    system_role: SystemRole = Field(
        default=SystemRole.UNKNOWN,
        description="What role the system should play",
    )


class MagnitudeInference(BaseModel):
    """Inferred scope and complexity of a capture."""

    scope: Scope = Field(default=Scope.ATOMIC, description="Size/scope of the item")
    complexity: int = Field(default=1, ge=1, le=5, description="Complexity score 1-5")
    dependencies: int = Field(default=0, ge=0, description="Number of inferred dependencies")
    uncertainty: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Uncertainty about scope (0=certain, 1=very uncertain)",
    )


class StateInference(BaseModel):
    """Inferred current state of a capture."""

    stage: Stage = Field(default=Stage.NOT_STARTED, description="Current lifecycle stage")
    bottleneck: str | None = Field(default=None, description="What's blocking progress, if any")
    energy_required: EnergyLevel = Field(
        default=EnergyLevel.UNKNOWN,
        description="Energy/effort required",
    )


# =============================================================================
# Core Output Models
# =============================================================================


class Capture(BaseModel):
    """A captured item (goal/plan/habit/task/reflection/blocker/metric)."""

    id: str = Field(default_factory=lambda: f"cap_{uuid4().hex[:8]}")
    type: CaptureType = Field(default=CaptureType.TASK, description="Type of captured item")
    title: str = Field(..., description="Normalized title in imperative form")
    raw_segment: str = Field(..., description="Original text segment")
    estimated_minutes: int = Field(default=15, ge=0, description="Estimated time in minutes")
    avoidance_weight: int = Field(default=1, ge=1, le=5, description="Emotional resistance 1-5")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Extraction confidence")
    ambiguities: list[str] = Field(default_factory=list, description="Clarifications needed")
    labels: TaxonomyLayer | None = Field(default=None, description="7-layer taxonomy")
    magnitude: MagnitudeInference | None = Field(default=None, description="Scope/complexity")
    state: StateInference | None = Field(default=None, description="Current state inference")
    needs_breakdown: bool = Field(default=False, description="Should be broken down")


class AtomicTask(BaseModel):
    """A micro-step derived from a capture."""

    id: str = Field(default_factory=lambda: f"task_{uuid4().hex[:8]}")
    parent_capture_id: str | None = Field(default=None, description="Parent capture ID")
    verb: str = Field(..., description="Action verb")
    object: str = Field(..., description="Object of the action")
    full_description: str | None = Field(default=None, description="Full task description")
    definition_of_done: str | None = Field(default=None, description="Completion criteria")
    estimated_minutes: int = Field(default=5, ge=1, le=30, description="Time estimate")
    energy_level: EnergyLevel = Field(default=EnergyLevel.LOW, description="Energy required")
    prerequisites: list[str] = Field(default_factory=list, description="Task IDs that must complete first")
    is_first_action: bool = Field(default=False, description="Recommended first step")
    is_physical: bool = Field(default=True, description="Involves physical movement")


class StateUpdate(BaseModel):
    """A database entity change from this turn."""

    entity_type: EntityType = Field(..., description="Type of entity affected")
    entity_id: str | None = Field(default=None, description="ID of the entity")
    temp_id: str | None = Field(default=None, description="Temp ID referencing capture/task")
    operation: Operation = Field(..., description="Type of change")
    changes: dict[str, Any] | None = Field(default=None, description="Field changes")


class ClarificationQuestion(BaseModel):
    """A clarification question for the user."""

    id: str = Field(default_factory=lambda: f"q_{uuid4().hex[:8]}")
    question: str = Field(..., description="The clarification question")
    target_capture_id: str = Field(..., description="Which capture this is about")
    question_type: QuestionType = Field(default=QuestionType.OTHER, description="Category")
    suggested_answers: list[str] = Field(default_factory=list, description="Suggested responses")


class UIBlock(BaseModel):
    """Structured rendering hint for the UI."""

    type: UIBlockType = Field(..., description="Type of UI block")
    data: dict[str, Any] = Field(default_factory=dict, description="Block-specific data")
    priority: int = Field(default=0, ge=0, description="Display priority (lower = higher)")


class PsychologicalInsight(BaseModel):
    """A detected psychological pattern."""

    pattern_name: str = Field(..., description="Name of the pattern")
    description: str = Field(..., description="What the AI noticed")
    suggested_strategy: str = Field(..., description="Recommended approach")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class CommandResult(BaseModel):
    """Command execution result."""

    command: str = Field(..., description="The command that was executed")
    message: str = Field(..., description="Response message")
    data: dict[str, Any] | None = Field(default=None, description="Optional data payload")


# =============================================================================
# Intent Classification
# =============================================================================


class IntentClassification(BaseModel):
    """Intent classification result."""

    type: IntentType = Field(..., description="Classified intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    reasoning: str | None = Field(default=None, description="Optional reasoning")


# =============================================================================
# Provenance
# =============================================================================


class TokenUsage(BaseModel):
    """Token usage for this turn."""

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)


class Provenance(BaseModel):
    """Metadata about how this output was generated."""

    model_id: str | None = Field(default=None, description="LLM model used")
    prompt_versions: dict[str, str] = Field(
        default_factory=dict,
        description="Map of prompt name to version used",
    )
    processing_time_ms: int = Field(default=0, ge=0, description="Processing time in ms")
    token_usage: TokenUsage | None = Field(default=None)


# =============================================================================
# Agent Output
# =============================================================================


class AgentOutput(BaseModel):
    """The core output payload."""

    raw_input: str = Field(..., description="Original user input")
    captures: list[Capture] = Field(default_factory=list, description="Extracted captures")
    atomic_tasks: list[AtomicTask] = Field(default_factory=list, description="Breakdown micro-steps")
    state_updates: list[StateUpdate] = Field(default_factory=list, description="Entity changes")
    questions: list[ClarificationQuestion] = Field(default_factory=list, description="Clarifications")
    insights: list[PsychologicalInsight] = Field(default_factory=list, description="Detected patterns")
    coaching_message: str | None = Field(default=None, description="Coaching response")
    command_result: CommandResult | None = Field(default=None, description="Command result")
    user_facing_summary: str | None = Field(default=None, description="Human-readable summary")
    ui_blocks: list[UIBlock] = Field(default_factory=list, description="UI rendering hints")
    overall_confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall confidence")
    cognitive_load: CognitiveLoadLevel = Field(
        default=CognitiveLoadLevel.ROUTINE,
        description="Appraised cognitive load",
    )
    needs_scaffolding: bool = Field(default=False, description="Whether AI should probe deeper")
    scaffolding_question: str | None = Field(default=None, description="Probe question")


# =============================================================================
# Top-Level Contract
# =============================================================================


class AgentOutputContract(BaseModel):
    """Standardized output contract for all agent turns.

    This is the top-level response structure returned by the agent API.
    Every turn, regardless of intent, returns this structure.
    """

    contract_version: str = Field(
        default="0.1.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version of this contract",
    )
    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this request",
    )
    trace_id: str | None = Field(default=None, description="Optional trace ID")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this response was generated",
    )
    intent: IntentClassification = Field(..., description="Intent classification")
    output: AgentOutput = Field(..., description="The core output payload")
    provenance: Provenance | None = Field(default=None, description="Generation metadata")

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


# =============================================================================
# Contract Version Constant
# =============================================================================

CONTRACT_VERSION = "0.1.0"
