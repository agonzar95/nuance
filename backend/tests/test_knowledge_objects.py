"""Tests for Knowledge Objects Service (MEM-001).

Tests knowledge object models, service operations, and writeback integration.
"""

from datetime import datetime, UTC, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.services.knowledge_objects import (
    KnowledgeObjectService,
    KnowledgeObjectType,
    KnowledgeObject,
    KnowledgeObjectCreate,
    KnowledgeObjectQuery,
    KnowledgeObjectSearchResult,
    get_knowledge_object_service,
)
from app.services.knowledge_writeback import (
    KnowledgeWritebackService,
    WritebackResult,
    get_knowledge_writeback_service,
)
from app.contracts.agent_output_v0 import (
    AgentOutputContract,
    AgentOutput,
    Capture,
    AtomicTask,
    PsychologicalInsight,
    IntentClassification,
    Provenance,
    TaxonomyLayer,
    MagnitudeInference,
    StateInference,
    IntentType,
    CaptureType,
    CognitiveLoadLevel,
    Scope,
    Stage,
    EnergyLevel,
    IntentLayer,
    SurvivalFunction,
    AgencyLevel,
    PsychSource,
    SystemRole,
)


# =============================================================================
# Knowledge Object Model Tests
# =============================================================================


class TestKnowledgeObjectCreate:
    """Tests for KnowledgeObjectCreate model."""

    def test_required_fields(self):
        """Create requires type and payload."""
        obj = KnowledgeObjectCreate(
            type=KnowledgeObjectType.TAXONOMY_LABEL,
            payload={"capture_id": "cap_123"},
        )
        assert obj.type == KnowledgeObjectType.TAXONOMY_LABEL
        assert obj.payload == {"capture_id": "cap_123"}

    def test_defaults(self):
        """Defaults are sensible."""
        obj = KnowledgeObjectCreate(
            type=KnowledgeObjectType.INSIGHT,
            payload={"pattern_name": "procrastination"},
        )
        assert obj.confidence == 0.5
        assert obj.importance == 50
        assert obj.source_message_id is None
        assert obj.source_action_id is None
        assert obj.natural_key is None
        assert obj.valid_to is None

    def test_confidence_bounds(self):
        """Confidence must be 0-1."""
        with pytest.raises(ValidationError):
            KnowledgeObjectCreate(
                type=KnowledgeObjectType.GOAL,
                payload={},
                confidence=1.5,
            )

    def test_importance_bounds(self):
        """Importance must be 0-100."""
        with pytest.raises(ValidationError):
            KnowledgeObjectCreate(
                type=KnowledgeObjectType.PLAN,
                payload={},
                importance=150,
            )


class TestKnowledgeObjectQuery:
    """Tests for KnowledgeObjectQuery model."""

    def test_defaults(self):
        """Query has sensible defaults."""
        query = KnowledgeObjectQuery()
        assert query.types is None
        assert query.source_action_id is None
        assert query.include_expired is False
        assert query.limit == 50
        assert query.offset == 0

    def test_limit_bounds(self):
        """Limit must be 1-100."""
        with pytest.raises(ValidationError):
            KnowledgeObjectQuery(limit=0)

        with pytest.raises(ValidationError):
            KnowledgeObjectQuery(limit=200)


class TestKnowledgeObjectType:
    """Tests for KnowledgeObjectType enum."""

    def test_all_types_present(self):
        """All expected types are defined."""
        expected = [
            "taxonomy_label",
            "breakdown",
            "insight",
            "checkpoint",
            "goal",
            "plan",
            "habit",
            "state_snapshot",
            "user_pattern",
            "coaching_note",
        ]
        actual = [t.value for t in KnowledgeObjectType]
        assert set(expected) == set(actual)


# =============================================================================
# Knowledge Object Service Tests
# =============================================================================


class TestKnowledgeObjectService:
    """Tests for KnowledgeObjectService."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Supabase client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create service with mock client."""
        svc = KnowledgeObjectService()
        svc._client = mock_client
        return svc

    def test_generate_natural_key(self, service):
        """Natural key generation is deterministic."""
        key1 = service._generate_natural_key(
            KnowledgeObjectType.TAXONOMY_LABEL,
            "user-123",
            source_message_id="msg-456",
        )
        key2 = service._generate_natural_key(
            KnowledgeObjectType.TAXONOMY_LABEL,
            "user-123",
            source_message_id="msg-456",
        )
        assert key1 == key2
        assert len(key1) == 32

    def test_generate_natural_key_differs_by_type(self, service):
        """Different types produce different keys."""
        key1 = service._generate_natural_key(
            KnowledgeObjectType.TAXONOMY_LABEL,
            "user-123",
        )
        key2 = service._generate_natural_key(
            KnowledgeObjectType.INSIGHT,
            "user-123",
        )
        assert key1 != key2

    def test_generate_natural_key_differs_by_user(self, service):
        """Different users produce different keys."""
        key1 = service._generate_natural_key(
            KnowledgeObjectType.GOAL,
            "user-123",
        )
        key2 = service._generate_natural_key(
            KnowledgeObjectType.GOAL,
            "user-456",
        )
        assert key1 != key2

    @pytest.mark.asyncio
    async def test_create_success(self, service, mock_client):
        """Create returns knowledge object on success."""
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{
                "id": "ko-123",
                "user_id": "user-123",
                "type": "taxonomy_label",
                "payload": {"capture_id": "cap-456"},
                "confidence": 0.8,
                "importance": 60,
                "source_message_id": None,
                "source_conversation_id": None,
                "source_action_id": None,
                "natural_key": "abc123",
                "valid_from": "2024-01-01T00:00:00+00:00",
                "valid_to": None,
                "model_id": None,
                "prompt_version": None,
                "request_id": None,
                "created_at": "2024-01-01T00:00:00+00:00",
                "updated_at": "2024-01-01T00:00:00+00:00",
            }]
        )

        obj = KnowledgeObjectCreate(
            type=KnowledgeObjectType.TAXONOMY_LABEL,
            payload={"capture_id": "cap-456"},
            confidence=0.8,
            importance=60,
        )

        result = await service.create("user-123", obj)

        assert result is not None
        assert result.id == "ko-123"
        assert result.type == KnowledgeObjectType.TAXONOMY_LABEL
        assert result.confidence == 0.8

    @pytest.mark.asyncio
    async def test_create_failure(self, service, mock_client):
        """Create returns None on failure."""
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB error")

        obj = KnowledgeObjectCreate(
            type=KnowledgeObjectType.GOAL,
            payload={"title": "Test goal"},
        )

        result = await service.create("user-123", obj)

        assert result is None

    @pytest.mark.asyncio
    async def test_upsert_calls_upsert(self, service, mock_client):
        """Upsert uses upsert operation with conflict resolution."""
        mock_client.table.return_value.upsert.return_value.execute.return_value = MagicMock(
            data=[{
                "id": "ko-123",
                "user_id": "user-123",
                "type": "insight",
                "payload": {"pattern_name": "test"},
                "confidence": 0.7,
                "importance": 50,
                "source_message_id": None,
                "source_conversation_id": None,
                "source_action_id": None,
                "natural_key": "key123",
                "valid_from": "2024-01-01T00:00:00+00:00",
                "valid_to": None,
                "model_id": None,
                "prompt_version": None,
                "request_id": None,
                "created_at": "2024-01-01T00:00:00+00:00",
                "updated_at": "2024-01-01T00:00:00+00:00",
            }]
        )

        obj = KnowledgeObjectCreate(
            type=KnowledgeObjectType.INSIGHT,
            payload={"pattern_name": "test"},
        )

        result = await service.upsert("user-123", obj)

        assert result is not None
        mock_client.table.return_value.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_with_type_filter(self, service, mock_client):
        """Query filters by type."""
        mock_result = MagicMock()
        mock_result.data = []
        mock_result.count = 0

        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.in_.return_value = mock_query
        mock_query.or_.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.execute.return_value = mock_result

        mock_client.table.return_value.select.return_value = mock_query

        query = KnowledgeObjectQuery(
            types=[KnowledgeObjectType.GOAL, KnowledgeObjectType.PLAN],
        )

        result = await service.query("user-123", query)

        assert isinstance(result, KnowledgeObjectSearchResult)
        mock_query.in_.assert_called_once()


# =============================================================================
# Knowledge Writeback Service Tests
# =============================================================================


class TestKnowledgeWritebackService:
    """Tests for KnowledgeWritebackService."""

    @pytest.fixture
    def mock_knowledge_service(self):
        """Create a mock knowledge service."""
        service = MagicMock(spec=KnowledgeObjectService)
        service.upsert = AsyncMock(return_value=MagicMock())
        return service

    @pytest.fixture
    def writeback_service(self, mock_knowledge_service):
        """Create writeback service with mock."""
        return KnowledgeWritebackService(knowledge_service=mock_knowledge_service)

    def _create_test_contract(
        self,
        captures: list[Capture] | None = None,
        atomic_tasks: list[AtomicTask] | None = None,
        insights: list[PsychologicalInsight] | None = None,
        coaching_message: str | None = None,
    ) -> AgentOutputContract:
        """Create a test contract for testing."""
        return AgentOutputContract(
            contract_version="0.1.0",
            request_id=str(uuid4()),
            intent=IntentClassification(type=IntentType.CAPTURE, confidence=0.9),
            output=AgentOutput(
                raw_input="test input",
                captures=captures or [],
                atomic_tasks=atomic_tasks or [],
                insights=insights or [],
                coaching_message=coaching_message,
                cognitive_load=CognitiveLoadLevel.ROUTINE,
            ),
            provenance=Provenance(
                model_id="claude-3-5-sonnet",
                prompt_versions={"extraction": "1.0.0"},
                processing_time_ms=150,
            ),
        )

    @pytest.mark.asyncio
    async def test_process_empty_contract(self, writeback_service, mock_knowledge_service):
        """Empty contract writes nothing."""
        contract = self._create_test_contract()

        result = await writeback_service.process_agent_output(
            user_id="user-123",
            contract=contract,
        )

        assert result.total_written == 0
        assert result.success is True
        mock_knowledge_service.upsert.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_capture_with_labels(self, writeback_service, mock_knowledge_service):
        """Capture with taxonomy labels writes taxonomy and state snapshot."""
        capture = Capture(
            id="cap_test",
            type=CaptureType.TASK,
            title="Test task",
            raw_segment="test",
            confidence=0.9,
            labels=TaxonomyLayer(
                intent_layer=IntentLayer.EXECUTE,
                cognitive_load=CognitiveLoadLevel.HIGH_FRICTION,
            ),
            magnitude=MagnitudeInference(
                scope=Scope.ATOMIC,
                complexity=2,
            ),
            state=StateInference(
                stage=Stage.NOT_STARTED,
                energy_required=EnergyLevel.MEDIUM,
            ),
        )

        contract = self._create_test_contract(captures=[capture])

        result = await writeback_service.process_agent_output(
            user_id="user-123",
            contract=contract,
        )

        # Should write taxonomy label and state snapshot
        assert result.taxonomy_labels_written == 1
        assert result.state_snapshots_written == 1
        assert mock_knowledge_service.upsert.call_count == 2

    @pytest.mark.asyncio
    async def test_process_capture_without_labels(self, writeback_service, mock_knowledge_service):
        """Capture without taxonomy only writes state snapshot if magnitude/state present."""
        capture = Capture(
            id="cap_test",
            type=CaptureType.TASK,
            title="Test task",
            raw_segment="test",
            confidence=0.9,
            labels=None,
            magnitude=None,
            state=None,
        )

        contract = self._create_test_contract(captures=[capture])

        result = await writeback_service.process_agent_output(
            user_id="user-123",
            contract=contract,
        )

        assert result.taxonomy_labels_written == 0
        assert result.state_snapshots_written == 0
        mock_knowledge_service.upsert.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_atomic_tasks(self, writeback_service, mock_knowledge_service):
        """Atomic tasks write a breakdown object."""
        tasks = [
            AtomicTask(
                id="task_1",
                parent_capture_id="cap_parent",
                verb="Open",
                object="laptop",
                estimated_minutes=2,
                is_first_action=True,
            ),
            AtomicTask(
                id="task_2",
                parent_capture_id="cap_parent",
                verb="Navigate",
                object="to website",
                estimated_minutes=1,
            ),
        ]

        contract = self._create_test_contract(atomic_tasks=tasks)

        result = await writeback_service.process_agent_output(
            user_id="user-123",
            contract=contract,
        )

        assert result.breakdowns_written == 1
        mock_knowledge_service.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_insights(self, writeback_service, mock_knowledge_service):
        """Insights write insight objects."""
        insights = [
            PsychologicalInsight(
                pattern_name="procrastination_loop",
                description="User tends to delay high-friction tasks",
                suggested_strategy="Start with smallest step",
                confidence=0.85,
            ),
        ]

        contract = self._create_test_contract(insights=insights)

        result = await writeback_service.process_agent_output(
            user_id="user-123",
            contract=contract,
        )

        assert result.insights_written == 1
        mock_knowledge_service.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_coaching_message(self, writeback_service, mock_knowledge_service):
        """Coaching message writes coaching note."""
        contract = self._create_test_contract(
            coaching_message="I hear you. Let's work through this together."
        )

        result = await writeback_service.process_agent_output(
            user_id="user-123",
            contract=contract,
        )

        assert result.coaching_notes_written == 1
        mock_knowledge_service.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_handles_errors_gracefully(self, writeback_service, mock_knowledge_service):
        """Errors don't stop processing other items."""
        mock_knowledge_service.upsert = AsyncMock(side_effect=Exception("DB error"))

        capture = Capture(
            id="cap_test",
            type=CaptureType.TASK,
            title="Test task",
            raw_segment="test",
            confidence=0.9,
            labels=TaxonomyLayer(),
        )

        contract = self._create_test_contract(captures=[capture])

        result = await writeback_service.process_agent_output(
            user_id="user-123",
            contract=contract,
        )

        assert result.success is False
        assert len(result.errors) > 0


class TestWritebackResult:
    """Tests for WritebackResult."""

    def test_total_written(self):
        """Total written sums all counts."""
        result = WritebackResult()
        result.taxonomy_labels_written = 3
        result.breakdowns_written = 1
        result.insights_written = 2
        result.state_snapshots_written = 3
        result.coaching_notes_written = 1

        assert result.total_written == 10

    def test_success_with_no_errors(self):
        """Success is True when no errors."""
        result = WritebackResult()
        assert result.success is True

    def test_success_with_errors(self):
        """Success is False when errors present."""
        result = WritebackResult()
        result.errors.append("test error")
        assert result.success is False

    def test_to_dict(self):
        """to_dict produces expected structure."""
        result = WritebackResult()
        result.taxonomy_labels_written = 2
        result.errors.append("error1")

        d = result.to_dict()

        assert d["total_written"] == 2
        assert d["taxonomy_labels"] == 2
        assert d["errors"] == ["error1"]
        assert d["success"] is False


# =============================================================================
# Idempotency Tests
# =============================================================================


class TestIdempotency:
    """Tests for idempotent behavior."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Supabase client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create service with mock client."""
        svc = KnowledgeObjectService()
        svc._client = mock_client
        return svc

    @pytest.mark.asyncio
    async def test_same_input_same_key(self, service, mock_client):
        """Same input produces same natural key for idempotency."""
        # Mock upsert to capture the data
        captured_data = []

        def capture_upsert(*args, **kwargs):
            captured_data.append(args[0] if args else kwargs)
            mock = MagicMock()
            mock.execute.return_value = MagicMock(data=[{
                "id": "ko-123",
                "user_id": "user-123",
                "type": "taxonomy_label",
                "payload": {"capture_id": "cap-456"},
                "confidence": 0.5,
                "importance": 50,
                "source_message_id": None,
                "source_conversation_id": None,
                "source_action_id": None,
                "natural_key": "testkey",
                "valid_from": "2024-01-01T00:00:00+00:00",
                "valid_to": None,
                "model_id": None,
                "prompt_version": None,
                "request_id": None,
                "created_at": "2024-01-01T00:00:00+00:00",
                "updated_at": "2024-01-01T00:00:00+00:00",
            }])
            return mock

        mock_client.table.return_value.upsert = capture_upsert

        obj = KnowledgeObjectCreate(
            type=KnowledgeObjectType.TAXONOMY_LABEL,
            payload={"capture_id": "cap-456"},
        )

        # Upsert twice
        await service.upsert("user-123", obj)
        await service.upsert("user-123", obj)

        # Both should have same natural_key
        assert len(captured_data) == 2
        assert captured_data[0]["natural_key"] == captured_data[1]["natural_key"]


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_get_knowledge_object_service_singleton(self):
        """get_knowledge_object_service returns same instance."""
        svc1 = get_knowledge_object_service()
        svc2 = get_knowledge_object_service()
        assert svc1 is svc2

    def test_get_knowledge_writeback_service_singleton(self):
        """get_knowledge_writeback_service returns same instance."""
        svc1 = get_knowledge_writeback_service()
        svc2 = get_knowledge_writeback_service()
        assert svc1 is svc2
