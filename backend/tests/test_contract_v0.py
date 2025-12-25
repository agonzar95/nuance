"""Tests for AgentOutputContract v0.

Tests contract models, mapping functions, and schema validation.
"""

import json
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.contracts import (
    AgentOutputContract,
    AgentOutput,
    Capture,
    AtomicTask,
    StateUpdate,
    ClarificationQuestion,
    UIBlock,
    PsychologicalInsight,
    CommandResult,
    IntentClassification,
    Provenance,
    TokenUsage,
    TaxonomyLayer,
    MagnitudeInference,
    StateInference,
    CONTRACT_VERSION,
    # Enums
    IntentType,
    CaptureType,
    CognitiveLoadLevel,
    Scope,
    Stage,
    EnergyLevel,
    EntityType,
    Operation,
    QuestionType,
    UIBlockType,
)
from app.contracts.mapper import (
    map_router_response_to_contract,
    map_enriched_action_to_capture,
    map_complexity_to_scope,
    map_cognitive_load,
    map_intent_to_type,
)
from app.services.intent import Intent
from app.services.intent_router import RouterResponse, CommandResponse
from app.services.extraction_orchestrator import OrchestrationResult, EnrichedAction
from app.models.database import ActionComplexity


# =============================================================================
# Contract Model Tests
# =============================================================================


class TestAgentOutputContract:
    """Tests for the top-level contract model."""

    def test_contract_version_required(self):
        """Contract must include version."""
        contract = AgentOutputContract(
            intent=IntentClassification(type=IntentType.CAPTURE, confidence=0.9),
            output=AgentOutput(raw_input="test"),
        )
        assert contract.contract_version == CONTRACT_VERSION

    def test_contract_generates_request_id(self):
        """Contract generates a request ID if not provided."""
        contract = AgentOutputContract(
            intent=IntentClassification(type=IntentType.CAPTURE, confidence=0.9),
            output=AgentOutput(raw_input="test"),
        )
        assert contract.request_id is not None
        assert len(contract.request_id) == 36  # UUID format

    def test_contract_generates_timestamp(self):
        """Contract generates timestamp if not provided."""
        contract = AgentOutputContract(
            intent=IntentClassification(type=IntentType.CAPTURE, confidence=0.9),
            output=AgentOutput(raw_input="test"),
        )
        assert contract.timestamp is not None
        assert isinstance(contract.timestamp, datetime)

    def test_contract_serialization(self):
        """Contract can be serialized to JSON."""
        contract = AgentOutputContract(
            contract_version="0.1.0",
            request_id=str(uuid4()),
            intent=IntentClassification(type=IntentType.CAPTURE, confidence=0.9),
            output=AgentOutput(
                raw_input="test input",
                captures=[
                    Capture(
                        id="cap_test",
                        type=CaptureType.TASK,
                        title="Test task",
                        raw_segment="test input",
                        confidence=0.85,
                    )
                ],
            ),
        )
        json_str = contract.model_dump_json()
        assert "contract_version" in json_str
        assert "0.1.0" in json_str
        assert "cap_test" in json_str


class TestCapture:
    """Tests for the Capture model."""

    def test_capture_defaults(self):
        """Capture has sensible defaults."""
        capture = Capture(
            title="Test task",
            raw_segment="test",
            confidence=0.9,
        )
        assert capture.type == CaptureType.TASK
        assert capture.estimated_minutes == 15
        assert capture.avoidance_weight == 1
        assert capture.needs_breakdown is False
        assert capture.ambiguities == []

    def test_capture_avoidance_bounds(self):
        """Avoidance weight must be 1-5."""
        with pytest.raises(ValidationError):
            Capture(
                title="Test",
                raw_segment="test",
                confidence=0.9,
                avoidance_weight=0,
            )

        with pytest.raises(ValidationError):
            Capture(
                title="Test",
                raw_segment="test",
                confidence=0.9,
                avoidance_weight=6,
            )

    def test_capture_confidence_bounds(self):
        """Confidence must be 0-1."""
        with pytest.raises(ValidationError):
            Capture(
                title="Test",
                raw_segment="test",
                confidence=1.5,
            )

    def test_capture_with_taxonomy(self):
        """Capture can include taxonomy labels."""
        capture = Capture(
            title="Test task",
            raw_segment="test",
            confidence=0.9,
            labels=TaxonomyLayer(
                cognitive_load=CognitiveLoadLevel.HIGH_FRICTION,
            ),
        )
        assert capture.labels is not None
        assert capture.labels.cognitive_load == CognitiveLoadLevel.HIGH_FRICTION


class TestAtomicTask:
    """Tests for the AtomicTask model."""

    def test_atomic_task_required_fields(self):
        """AtomicTask requires verb and object."""
        task = AtomicTask(
            verb="Open",
            object="laptop",
        )
        assert task.verb == "Open"
        assert task.object == "laptop"
        assert task.estimated_minutes == 5

    def test_atomic_task_time_bounds(self):
        """AtomicTask time must be 1-30 minutes."""
        with pytest.raises(ValidationError):
            AtomicTask(
                verb="Do",
                object="thing",
                estimated_minutes=0,
            )

        with pytest.raises(ValidationError):
            AtomicTask(
                verb="Do",
                object="thing",
                estimated_minutes=60,
            )


class TestStateUpdate:
    """Tests for the StateUpdate model."""

    def test_state_update_create(self):
        """StateUpdate for creation."""
        update = StateUpdate(
            entity_type=EntityType.ACTION,
            temp_id="cap_123",
            operation=Operation.CREATED,
            changes={"title": "New task"},
        )
        assert update.entity_id is None
        assert update.temp_id == "cap_123"
        assert update.operation == Operation.CREATED


# =============================================================================
# Mapper Tests
# =============================================================================


class TestMapper:
    """Tests for the contract mapper functions."""

    def test_map_complexity_to_scope(self):
        """Complexity maps to scope correctly."""
        assert map_complexity_to_scope(ActionComplexity.ATOMIC) == Scope.ATOMIC
        assert map_complexity_to_scope(ActionComplexity.COMPOSITE) == Scope.COMPOSITE
        assert map_complexity_to_scope(ActionComplexity.PROJECT) == Scope.PROJECT

    def test_map_cognitive_load(self):
        """Cognitive load maps correctly."""
        assert map_cognitive_load("ROUTINE") == CognitiveLoadLevel.ROUTINE
        assert map_cognitive_load("HIGH_FRICTION") == CognitiveLoadLevel.HIGH_FRICTION
        assert map_cognitive_load("routine") == CognitiveLoadLevel.ROUTINE

    def test_map_intent_to_type(self):
        """Intent maps to IntentType correctly."""
        assert map_intent_to_type(Intent.CAPTURE) == IntentType.CAPTURE
        assert map_intent_to_type(Intent.COACHING) == IntentType.COACHING
        assert map_intent_to_type(Intent.COMMAND) == IntentType.COMMAND
        assert map_intent_to_type(Intent.CLARIFY) == IntentType.CLARIFY

    def test_map_enriched_action_to_capture(self):
        """EnrichedAction maps to Capture correctly."""
        action = EnrichedAction(
            title="Call mom",
            estimated_minutes=15,
            raw_segment="I need to call mom",
            avoidance_weight=2,
            complexity=ActionComplexity.ATOMIC,
            needs_breakdown=False,
            confidence=0.92,
            ambiguities=[],
            cognitive_load="ROUTINE",
        )

        capture = map_enriched_action_to_capture(action)

        assert capture.title == "Call mom"
        assert capture.estimated_minutes == 15
        assert capture.avoidance_weight == 2
        assert capture.confidence == 0.92
        assert capture.type == CaptureType.TASK
        assert capture.magnitude is not None
        assert capture.magnitude.scope == Scope.ATOMIC

    def test_map_router_response_capture(self):
        """RouterResponse with extraction maps correctly."""
        extraction = OrchestrationResult(
            actions=[
                EnrichedAction(
                    title="Buy groceries",
                    estimated_minutes=30,
                    raw_segment="buy groceries",
                    avoidance_weight=1,
                    complexity=ActionComplexity.ATOMIC,
                    needs_breakdown=False,
                    confidence=0.95,
                    ambiguities=[],
                    cognitive_load="ROUTINE",
                )
            ],
            raw_input="I need to buy groceries",
            overall_confidence=0.95,
            needs_validation=False,
            cognitive_load="ROUTINE",
            needs_scaffolding=False,
            scaffolding_question=None,
        )

        response = RouterResponse(
            intent=Intent.CAPTURE,
            intent_confidence=0.9,
            response_type="capture",
            extraction=extraction,
        )

        contract = map_router_response_to_contract(
            response=response,
            raw_input="I need to buy groceries",
            processing_time_ms=150,
        )

        assert contract.contract_version == CONTRACT_VERSION
        assert contract.intent.type == IntentType.CAPTURE
        assert contract.intent.confidence == 0.9
        assert len(contract.output.captures) == 1
        assert contract.output.captures[0].title == "Buy groceries"
        assert contract.output.cognitive_load == CognitiveLoadLevel.ROUTINE
        assert contract.provenance is not None
        assert contract.provenance.processing_time_ms == 150

    def test_map_router_response_coaching(self):
        """RouterResponse with coaching maps correctly."""
        response = RouterResponse(
            intent=Intent.COACHING,
            intent_confidence=0.88,
            response_type="coaching",
            coaching_response="I hear you. Let's work through this together.",
        )

        contract = map_router_response_to_contract(
            response=response,
            raw_input="I'm feeling stuck",
        )

        assert contract.intent.type == IntentType.COACHING
        assert contract.output.coaching_message == "I hear you. Let's work through this together."
        assert len(contract.output.captures) == 0

    def test_map_router_response_command(self):
        """RouterResponse with command maps correctly."""
        response = RouterResponse(
            intent=Intent.COMMAND,
            intent_confidence=1.0,
            response_type="command",
            command_response=CommandResponse(
                command="/help",
                message="Available commands: /start, /help, /status",
                data={"commands": ["/start", "/help", "/status"]},
            ),
        )

        contract = map_router_response_to_contract(
            response=response,
            raw_input="/help",
        )

        assert contract.intent.type == IntentType.COMMAND
        assert contract.output.command_result is not None
        assert contract.output.command_result.command == "/help"
        assert contract.output.command_result.message == "Available commands: /start, /help, /status"


# =============================================================================
# Schema Validation Tests
# =============================================================================


class TestSchemaValidation:
    """Tests for JSON Schema validation of example payloads."""

    @pytest.fixture
    def examples_dir(self) -> Path:
        """Get the examples directory."""
        return Path(__file__).parent.parent.parent / "docs" / "examples"

    def test_capture_example_valid(self, examples_dir: Path):
        """CAPTURE example payload validates against contract."""
        example_path = examples_dir / "contract_v0_capture.json"
        if not example_path.exists():
            pytest.skip("Example file not found")

        with open(example_path) as f:
            data = json.load(f)

        # Remove non-schema fields
        data.pop("$schema", None)
        data.pop("_description", None)

        # Parse as contract (validates structure)
        contract = AgentOutputContract(**data)
        assert contract.contract_version == "0.1.0"
        assert contract.intent.type == IntentType.CAPTURE
        assert len(contract.output.captures) == 3

    def test_coaching_example_valid(self, examples_dir: Path):
        """COACHING example payload validates against contract."""
        example_path = examples_dir / "contract_v0_coaching.json"
        if not example_path.exists():
            pytest.skip("Example file not found")

        with open(example_path) as f:
            data = json.load(f)

        data.pop("$schema", None)
        data.pop("_description", None)

        contract = AgentOutputContract(**data)
        assert contract.contract_version == "0.1.0"
        assert contract.intent.type == IntentType.COACHING
        assert contract.output.coaching_message is not None

    def test_clarify_example_valid(self, examples_dir: Path):
        """CLARIFY example payload validates against contract."""
        example_path = examples_dir / "contract_v0_clarify.json"
        if not example_path.exists():
            pytest.skip("Example file not found")

        with open(example_path) as f:
            data = json.load(f)

        data.pop("$schema", None)
        data.pop("_description", None)

        contract = AgentOutputContract(**data)
        assert contract.contract_version == "0.1.0"
        assert contract.intent.type == IntentType.CLARIFY
        assert len(contract.output.questions) > 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestContractIntegration:
    """Integration tests for contract usage."""

    def test_full_capture_flow(self):
        """Test a complete capture flow produces valid contract."""
        # Simulate extraction result
        extraction = OrchestrationResult(
            actions=[
                EnrichedAction(
                    title="Call insurance",
                    estimated_minutes=30,
                    raw_segment="call the insurance company",
                    avoidance_weight=4,
                    complexity=ActionComplexity.ATOMIC,
                    needs_breakdown=True,
                    confidence=0.85,
                    ambiguities=["Which insurance?"],
                    cognitive_load="HIGH_FRICTION",
                ),
                EnrichedAction(
                    title="Buy milk",
                    estimated_minutes=15,
                    raw_segment="buy milk",
                    avoidance_weight=1,
                    complexity=ActionComplexity.ATOMIC,
                    needs_breakdown=False,
                    confidence=0.98,
                    ambiguities=[],
                    cognitive_load="ROUTINE",
                ),
            ],
            raw_input="I need to call the insurance company and buy milk",
            overall_confidence=0.91,
            needs_validation=False,
            cognitive_load="HIGH_FRICTION",
            needs_scaffolding=True,
            scaffolding_question="What part of the insurance call feels heaviest?",
        )

        response = RouterResponse(
            intent=Intent.CAPTURE,
            intent_confidence=0.95,
            response_type="capture",
            extraction=extraction,
        )

        contract = map_router_response_to_contract(
            response=response,
            raw_input="I need to call the insurance company and buy milk",
            processing_time_ms=250,
        )

        # Validate contract structure
        assert contract.contract_version == CONTRACT_VERSION
        assert contract.request_id is not None
        assert contract.timestamp is not None

        # Validate intent
        assert contract.intent.type == IntentType.CAPTURE
        assert contract.intent.confidence == 0.95

        # Validate captures
        assert len(contract.output.captures) == 2
        assert contract.output.captures[0].title == "Call insurance"
        assert contract.output.captures[0].avoidance_weight == 4
        assert contract.output.captures[0].needs_breakdown is True
        assert contract.output.captures[1].title == "Buy milk"
        assert contract.output.captures[1].avoidance_weight == 1

        # Validate state updates
        assert len(contract.output.state_updates) == 2
        assert contract.output.state_updates[0].operation == Operation.CREATED

        # Validate scaffolding
        assert contract.output.needs_scaffolding is True
        assert contract.output.scaffolding_question is not None

        # Validate UI blocks
        assert len(contract.output.ui_blocks) > 0

        # Validate provenance
        assert contract.provenance is not None
        assert contract.provenance.processing_time_ms == 250

        # Test serialization roundtrip
        json_str = contract.model_dump_json()
        parsed = AgentOutputContract.model_validate_json(json_str)
        assert parsed.contract_version == contract.contract_version
        assert len(parsed.output.captures) == 2
