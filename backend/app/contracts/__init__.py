"""Contracts module for API response structures."""

from app.contracts.agent_output_v0 import (
    # Contract
    AgentOutputContract,
    CONTRACT_VERSION,
    # Enums
    IntentType,
    CaptureType,
    IntentLayer,
    SurvivalFunction,
    CognitiveLoadLevel,
    TimeHorizon,
    AgencyLevel,
    PsychSource,
    SystemRole,
    Scope,
    Stage,
    EnergyLevel,
    EntityType,
    Operation,
    QuestionType,
    UIBlockType,
    # Models
    TaxonomyLayer,
    MagnitudeInference,
    StateInference,
    Capture,
    AtomicTask,
    StateUpdate,
    ClarificationQuestion,
    UIBlock,
    PsychologicalInsight,
    CommandResult,
    IntentClassification,
    TokenUsage,
    Provenance,
    AgentOutput,
)

from app.contracts.mapper import (
    ContractMapper,
    get_contract_mapper,
    map_router_response_to_contract,
    map_enriched_action_to_capture,
)

__all__ = [
    # Contract
    "AgentOutputContract",
    "CONTRACT_VERSION",
    # Enums
    "IntentType",
    "CaptureType",
    "IntentLayer",
    "SurvivalFunction",
    "CognitiveLoadLevel",
    "TimeHorizon",
    "AgencyLevel",
    "PsychSource",
    "SystemRole",
    "Scope",
    "Stage",
    "EnergyLevel",
    "EntityType",
    "Operation",
    "QuestionType",
    "UIBlockType",
    # Models
    "TaxonomyLayer",
    "MagnitudeInference",
    "StateInference",
    "Capture",
    "AtomicTask",
    "StateUpdate",
    "ClarificationQuestion",
    "UIBlock",
    "PsychologicalInsight",
    "CommandResult",
    "IntentClassification",
    "TokenUsage",
    "Provenance",
    "AgentOutput",
    # Mapper
    "ContractMapper",
    "get_contract_mapper",
    "map_router_response_to_contract",
    "map_enriched_action_to_capture",
]
