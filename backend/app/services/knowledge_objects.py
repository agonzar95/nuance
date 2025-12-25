"""Knowledge Objects Service (MEM-001).

Persistence layer for derived knowledge objects (memory/bookkeeping).
Stores taxonomy labels, breakdowns, insights, checkpoints, goals/plans/habits
as JSONB objects linked to existing entities.
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
import hashlib

from pydantic import BaseModel, Field
import structlog

from app.clients.supabase import get_client

logger = structlog.get_logger()


# =============================================================================
# Enums
# =============================================================================


class KnowledgeObjectType(str, Enum):
    """Types of knowledge objects that can be stored."""

    TAXONOMY_LABEL = "taxonomy_label"
    BREAKDOWN = "breakdown"
    INSIGHT = "insight"
    CHECKPOINT = "checkpoint"
    GOAL = "goal"
    PLAN = "plan"
    HABIT = "habit"
    STATE_SNAPSHOT = "state_snapshot"
    USER_PATTERN = "user_pattern"
    COACHING_NOTE = "coaching_note"


# =============================================================================
# Pydantic Models
# =============================================================================


class KnowledgeObjectCreate(BaseModel):
    """Model for creating a knowledge object."""

    type: KnowledgeObjectType = Field(..., description="Type of knowledge object")
    payload: dict[str, Any] = Field(..., description="Type-specific JSONB payload")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score")
    importance: int = Field(default=50, ge=0, le=100, description="Importance score")
    source_message_id: str | None = Field(default=None, description="Source message ID")
    source_conversation_id: str | None = Field(default=None, description="Source conversation ID")
    source_action_id: str | None = Field(default=None, description="Source action ID")
    natural_key: str | None = Field(default=None, description="Idempotency key")
    valid_from: datetime | None = Field(default=None, description="Validity start")
    valid_to: datetime | None = Field(default=None, description="Validity end (TTL)")
    model_id: str | None = Field(default=None, description="LLM model used")
    prompt_version: str | None = Field(default=None, description="Prompt version")
    request_id: str | None = Field(default=None, description="Request ID for tracing")


class KnowledgeObject(BaseModel):
    """Full knowledge object model with all fields."""

    id: str
    user_id: str
    type: KnowledgeObjectType
    payload: dict[str, Any]
    confidence: float
    importance: int
    source_message_id: str | None = None
    source_conversation_id: str | None = None
    source_action_id: str | None = None
    natural_key: str | None = None
    valid_from: datetime
    valid_to: datetime | None = None
    model_id: str | None = None
    prompt_version: str | None = None
    request_id: str | None = None
    created_at: datetime
    updated_at: datetime


class KnowledgeObjectQuery(BaseModel):
    """Query parameters for searching knowledge objects."""

    types: list[KnowledgeObjectType] | None = Field(default=None, description="Filter by types")
    source_action_id: str | None = Field(default=None, description="Filter by action")
    source_conversation_id: str | None = Field(default=None, description="Filter by conversation")
    source_message_id: str | None = Field(default=None, description="Filter by message")
    from_date: datetime | None = Field(default=None, description="Filter from date")
    to_date: datetime | None = Field(default=None, description="Filter to date")
    include_expired: bool = Field(default=False, description="Include expired objects")
    payload_contains: dict[str, Any] | None = Field(default=None, description="JSONB contains filter")
    limit: int = Field(default=50, ge=1, le=100, description="Max results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class KnowledgeObjectSearchResult(BaseModel):
    """Result from a knowledge object search."""

    objects: list[KnowledgeObject]
    total: int
    has_more: bool


# =============================================================================
# Payload Schemas (for documentation and validation)
# =============================================================================


class TaxonomyLabelPayload(BaseModel):
    """Payload schema for taxonomy_label type."""

    capture_id: str = Field(..., description="Associated capture ID")
    intent_layer: str | None = None
    survival_function: str | None = None
    cognitive_load: str | None = None
    time_horizon: str | None = None
    agency_level: str | None = None
    psych_source: str | None = None
    system_role: str | None = None


class BreakdownPayload(BaseModel):
    """Payload schema for breakdown type."""

    parent_capture_id: str = Field(..., description="Parent capture/action ID")
    parent_title: str = Field(..., description="Parent task title")
    steps: list[dict[str, Any]] = Field(default_factory=list, description="Atomic task steps")
    total_estimated_minutes: int = Field(default=0, description="Total time estimate")


class InsightPayload(BaseModel):
    """Payload schema for insight type."""

    pattern_name: str = Field(..., description="Name of detected pattern")
    description: str = Field(..., description="What was noticed")
    suggested_strategy: str = Field(..., description="Recommended approach")
    trigger_context: str | None = Field(default=None, description="What triggered detection")


class CheckpointPayload(BaseModel):
    """Payload schema for checkpoint type."""

    conversation_id: str = Field(..., description="Conversation being checkpointed")
    summary: str = Field(..., description="Conversation summary")
    key_points: list[str] = Field(default_factory=list, description="Key takeaways")
    next_steps: list[str] = Field(default_factory=list, description="Suggested next steps")
    message_count: int = Field(default=0, description="Messages in conversation")


class GoalPayload(BaseModel):
    """Payload schema for goal type."""

    title: str = Field(..., description="Goal title")
    description: str | None = Field(default=None, description="Goal description")
    target_date: str | None = Field(default=None, description="Target completion date")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    related_action_ids: list[str] = Field(default_factory=list, description="Related actions")


class PlanPayload(BaseModel):
    """Payload schema for plan type."""

    title: str = Field(..., description="Plan title")
    goal_id: str | None = Field(default=None, description="Associated goal ID")
    steps: list[dict[str, Any]] = Field(default_factory=list, description="Plan steps")
    current_step: int = Field(default=0, description="Current step index")


class HabitPayload(BaseModel):
    """Payload schema for habit type."""

    title: str = Field(..., description="Habit title")
    frequency: str = Field(default="daily", description="Frequency: daily/weekly/monthly")
    streak: int = Field(default=0, description="Current streak")
    last_completed: str | None = Field(default=None, description="Last completion date")
    trigger: str | None = Field(default=None, description="Habit trigger")
    reward: str | None = Field(default=None, description="Habit reward")


# =============================================================================
# Service
# =============================================================================


class KnowledgeObjectService:
    """Service for persisting and querying knowledge objects.

    Uses the service role key to bypass RLS for backend operations.
    All mutations require a user_id for proper data isolation.
    """

    def __init__(self) -> None:
        """Initialize the service."""
        self._client = None

    @property
    def client(self):
        """Lazy-load the Supabase client."""
        if self._client is None:
            self._client = get_client()
        return self._client

    def _generate_natural_key(
        self,
        ko_type: KnowledgeObjectType,
        user_id: str,
        source_message_id: str | None = None,
        source_action_id: str | None = None,
        payload_key: str | None = None,
    ) -> str:
        """Generate a deterministic natural key for idempotency.

        Args:
            ko_type: Knowledge object type.
            user_id: User ID.
            source_message_id: Optional message ID.
            source_action_id: Optional action ID.
            payload_key: Optional key from payload (e.g., capture_id).

        Returns:
            A deterministic hash string.
        """
        parts = [ko_type.value, user_id]

        if source_message_id:
            parts.append(f"msg:{source_message_id}")
        if source_action_id:
            parts.append(f"action:{source_action_id}")
        if payload_key:
            parts.append(f"payload:{payload_key}")

        key_string = "|".join(parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]

    async def create(
        self,
        user_id: str,
        obj: KnowledgeObjectCreate,
    ) -> KnowledgeObject | None:
        """Create a new knowledge object.

        Args:
            user_id: The user's ID.
            obj: The object to create.

        Returns:
            Created knowledge object or None if failed.
        """
        try:
            # Generate natural key if not provided
            natural_key = obj.natural_key
            if not natural_key:
                payload_key = obj.payload.get("capture_id") or obj.payload.get("conversation_id")
                natural_key = self._generate_natural_key(
                    obj.type,
                    user_id,
                    obj.source_message_id,
                    obj.source_action_id,
                    payload_key,
                )

            data = {
                "user_id": user_id,
                "type": obj.type.value,
                "payload": obj.payload,
                "confidence": obj.confidence,
                "importance": obj.importance,
                "source_message_id": obj.source_message_id,
                "source_conversation_id": obj.source_conversation_id,
                "source_action_id": obj.source_action_id,
                "natural_key": natural_key,
                "valid_from": (obj.valid_from or datetime.now(UTC)).isoformat(),
                "valid_to": obj.valid_to.isoformat() if obj.valid_to else None,
                "model_id": obj.model_id,
                "prompt_version": obj.prompt_version,
                "request_id": obj.request_id,
            }

            result = self.client.table("knowledge_objects").insert(data).execute()

            if result.data:
                logger.debug(
                    "Knowledge object created",
                    id=result.data[0].get("id"),
                    type=obj.type.value,
                    user_id=user_id,
                )
                return self._parse_row(result.data[0])

            return None

        except Exception as e:
            logger.error("Failed to create knowledge object", error=str(e), type=obj.type.value)
            return None

    async def upsert(
        self,
        user_id: str,
        obj: KnowledgeObjectCreate,
    ) -> KnowledgeObject | None:
        """Create or update a knowledge object based on natural key.

        Uses the natural_key constraint for idempotent operations.

        Args:
            user_id: The user's ID.
            obj: The object to upsert.

        Returns:
            Upserted knowledge object or None if failed.
        """
        try:
            # Generate natural key if not provided
            natural_key = obj.natural_key
            if not natural_key:
                payload_key = obj.payload.get("capture_id") or obj.payload.get("conversation_id")
                natural_key = self._generate_natural_key(
                    obj.type,
                    user_id,
                    obj.source_message_id,
                    obj.source_action_id,
                    payload_key,
                )

            data = {
                "user_id": user_id,
                "type": obj.type.value,
                "payload": obj.payload,
                "confidence": obj.confidence,
                "importance": obj.importance,
                "source_message_id": obj.source_message_id,
                "source_conversation_id": obj.source_conversation_id,
                "source_action_id": obj.source_action_id,
                "natural_key": natural_key,
                "valid_from": (obj.valid_from or datetime.now(UTC)).isoformat(),
                "valid_to": obj.valid_to.isoformat() if obj.valid_to else None,
                "model_id": obj.model_id,
                "prompt_version": obj.prompt_version,
                "request_id": obj.request_id,
            }

            result = (
                self.client.table("knowledge_objects")
                .upsert(data, on_conflict="user_id,type,natural_key")
                .execute()
            )

            if result.data:
                logger.debug(
                    "Knowledge object upserted",
                    id=result.data[0].get("id"),
                    type=obj.type.value,
                    user_id=user_id,
                )
                return self._parse_row(result.data[0])

            return None

        except Exception as e:
            logger.error("Failed to upsert knowledge object", error=str(e), type=obj.type.value)
            return None

    async def upsert_many(
        self,
        user_id: str,
        objects: list[KnowledgeObjectCreate],
    ) -> list[KnowledgeObject]:
        """Upsert multiple knowledge objects.

        Args:
            user_id: The user's ID.
            objects: Objects to upsert.

        Returns:
            List of successfully upserted objects.
        """
        results = []
        for obj in objects:
            result = await self.upsert(user_id, obj)
            if result:
                results.append(result)
        return results

    async def get_by_id(self, user_id: str, obj_id: str) -> KnowledgeObject | None:
        """Get a knowledge object by ID.

        Args:
            user_id: The user's ID (for RLS check).
            obj_id: The object ID.

        Returns:
            Knowledge object or None.
        """
        try:
            result = (
                self.client.table("knowledge_objects")
                .select("*")
                .eq("id", obj_id)
                .eq("user_id", user_id)
                .execute()
            )

            if result.data:
                return self._parse_row(result.data[0])
            return None

        except Exception as e:
            logger.error("Failed to get knowledge object", error=str(e), id=obj_id)
            return None

    async def query(
        self,
        user_id: str,
        query: KnowledgeObjectQuery,
    ) -> KnowledgeObjectSearchResult:
        """Query knowledge objects with filters.

        Args:
            user_id: The user's ID.
            query: Query parameters.

        Returns:
            Search result with matching objects.
        """
        try:
            q = (
                self.client.table("knowledge_objects")
                .select("*", count="exact")
                .eq("user_id", user_id)
            )

            # Type filter
            if query.types:
                type_values = [t.value for t in query.types]
                q = q.in_("type", type_values)

            # Source filters
            if query.source_action_id:
                q = q.eq("source_action_id", query.source_action_id)
            if query.source_conversation_id:
                q = q.eq("source_conversation_id", query.source_conversation_id)
            if query.source_message_id:
                q = q.eq("source_message_id", query.source_message_id)

            # Date range filters
            if query.from_date:
                q = q.gte("created_at", query.from_date.isoformat())
            if query.to_date:
                q = q.lte("created_at", query.to_date.isoformat())

            # Expiry filter
            if not query.include_expired:
                # Include objects with no expiry OR expiry in the future
                q = q.or_("valid_to.is.null,valid_to.gt.now()")

            # JSONB contains filter (if supported)
            if query.payload_contains:
                q = q.contains("payload", query.payload_contains)

            # Pagination and ordering
            q = q.order("created_at", desc=True).range(
                query.offset, query.offset + query.limit - 1
            )

            result = q.execute()

            objects = [self._parse_row(row) for row in result.data] if result.data else []
            total = result.count or len(objects)
            has_more = query.offset + len(objects) < total

            return KnowledgeObjectSearchResult(
                objects=objects,
                total=total,
                has_more=has_more,
            )

        except Exception as e:
            logger.error("Failed to query knowledge objects", error=str(e))
            return KnowledgeObjectSearchResult(objects=[], total=0, has_more=False)

    async def get_by_action(
        self,
        user_id: str,
        action_id: str,
        types: list[KnowledgeObjectType] | None = None,
    ) -> list[KnowledgeObject]:
        """Get all knowledge objects for an action.

        Args:
            user_id: The user's ID.
            action_id: The action ID.
            types: Optional type filter.

        Returns:
            List of knowledge objects.
        """
        query = KnowledgeObjectQuery(
            source_action_id=action_id,
            types=types,
        )
        result = await self.query(user_id, query)
        return result.objects

    async def get_by_type(
        self,
        user_id: str,
        ko_type: KnowledgeObjectType,
        limit: int = 50,
    ) -> list[KnowledgeObject]:
        """Get knowledge objects by type.

        Args:
            user_id: The user's ID.
            ko_type: The object type.
            limit: Max results.

        Returns:
            List of knowledge objects.
        """
        query = KnowledgeObjectQuery(types=[ko_type], limit=limit)
        result = await self.query(user_id, query)
        return result.objects

    async def get_active_goals(self, user_id: str) -> list[KnowledgeObject]:
        """Get active goals for a user (convenience method).

        Args:
            user_id: The user's ID.

        Returns:
            List of active goal objects.
        """
        return await self.get_by_type(user_id, KnowledgeObjectType.GOAL)

    async def get_latest_insights(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[KnowledgeObject]:
        """Get latest insights for a user.

        Args:
            user_id: The user's ID.
            limit: Max results.

        Returns:
            List of insight objects.
        """
        return await self.get_by_type(user_id, KnowledgeObjectType.INSIGHT, limit=limit)

    async def search_payload(
        self,
        user_id: str,
        query_text: str,
        types: list[KnowledgeObjectType] | None = None,
        limit: int = 20,
    ) -> list[KnowledgeObject]:
        """Search knowledge objects by payload content (basic text search).

        Note: This is a simple contains search. For full-text search,
        consider adding a tsvector column or using pg_trgm extension.

        Args:
            user_id: The user's ID.
            query_text: Text to search for.
            types: Optional type filter.
            limit: Max results.

        Returns:
            List of matching objects.
        """
        try:
            q = (
                self.client.table("knowledge_objects")
                .select("*")
                .eq("user_id", user_id)
                .ilike("payload::text", f"%{query_text}%")
            )

            if types:
                type_values = [t.value for t in types]
                q = q.in_("type", type_values)

            q = q.order("created_at", desc=True).limit(limit)

            result = q.execute()

            return [self._parse_row(row) for row in result.data] if result.data else []

        except Exception as e:
            logger.error("Failed to search knowledge objects", error=str(e))
            return []

    async def expire(
        self,
        user_id: str,
        obj_id: str,
    ) -> bool:
        """Mark a knowledge object as expired.

        Args:
            user_id: The user's ID.
            obj_id: The object ID.

        Returns:
            True if successful.
        """
        try:
            result = (
                self.client.table("knowledge_objects")
                .update({"valid_to": datetime.now(UTC).isoformat()})
                .eq("id", obj_id)
                .eq("user_id", user_id)
                .execute()
            )

            return bool(result.data)

        except Exception as e:
            logger.error("Failed to expire knowledge object", error=str(e), id=obj_id)
            return False

    async def delete(
        self,
        user_id: str,
        obj_id: str,
    ) -> bool:
        """Delete a knowledge object.

        Args:
            user_id: The user's ID.
            obj_id: The object ID.

        Returns:
            True if successful.
        """
        try:
            result = (
                self.client.table("knowledge_objects")
                .delete()
                .eq("id", obj_id)
                .eq("user_id", user_id)
                .execute()
            )

            return bool(result.data)

        except Exception as e:
            logger.error("Failed to delete knowledge object", error=str(e), id=obj_id)
            return False

    def _parse_row(self, row: dict[str, Any]) -> KnowledgeObject:
        """Parse a database row into a KnowledgeObject."""
        return KnowledgeObject(
            id=row["id"],
            user_id=row["user_id"],
            type=KnowledgeObjectType(row["type"]),
            payload=row["payload"],
            confidence=float(row["confidence"]),
            importance=row["importance"],
            source_message_id=row.get("source_message_id"),
            source_conversation_id=row.get("source_conversation_id"),
            source_action_id=row.get("source_action_id"),
            natural_key=row.get("natural_key"),
            valid_from=datetime.fromisoformat(row["valid_from"].replace("Z", "+00:00")),
            valid_to=datetime.fromisoformat(row["valid_to"].replace("Z", "+00:00")) if row.get("valid_to") else None,
            model_id=row.get("model_id"),
            prompt_version=row.get("prompt_version"),
            request_id=row.get("request_id"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")),
        )


# =============================================================================
# Factory Function
# =============================================================================


_service: KnowledgeObjectService | None = None


def get_knowledge_object_service() -> KnowledgeObjectService:
    """Get or create the knowledge object service singleton."""
    global _service
    if _service is None:
        _service = KnowledgeObjectService()
    return _service
