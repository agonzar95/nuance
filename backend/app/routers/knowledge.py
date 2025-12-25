"""Knowledge Objects API Router (MEM-001).

Query endpoints for derived knowledge objects (memory/bookkeeping).
Provides search by type, time range, and related entities.
"""

from datetime import datetime, UTC
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
import structlog

from app.auth import CurrentUser
from app.services.knowledge_objects import (
    KnowledgeObjectService,
    KnowledgeObjectType,
    KnowledgeObject,
    KnowledgeObjectQuery,
    KnowledgeObjectSearchResult,
    get_knowledge_object_service,
)

logger = structlog.get_logger()


# =============================================================================
# Router Setup
# =============================================================================

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


# =============================================================================
# Response Models
# =============================================================================


class KnowledgeObjectResponse(BaseModel):
    """Single knowledge object response."""

    id: str
    type: str
    payload: dict[str, Any]
    confidence: float
    importance: int
    source_action_id: str | None = None
    source_conversation_id: str | None = None
    source_message_id: str | None = None
    valid_from: datetime
    valid_to: datetime | None = None
    created_at: datetime
    updated_at: datetime


class KnowledgeListResponse(BaseModel):
    """Paginated list of knowledge objects."""

    objects: list[KnowledgeObjectResponse]
    total: int
    has_more: bool
    cursor: str | None = None


class LatestStateResponse(BaseModel):
    """Latest derived state for active projects/goals."""

    goals: list[KnowledgeObjectResponse]
    plans: list[KnowledgeObjectResponse]
    habits: list[KnowledgeObjectResponse]
    recent_insights: list[KnowledgeObjectResponse]
    total_knowledge_objects: int


# =============================================================================
# Helper Functions
# =============================================================================


def _to_response(obj: KnowledgeObject) -> KnowledgeObjectResponse:
    """Convert KnowledgeObject to response model."""
    return KnowledgeObjectResponse(
        id=obj.id,
        type=obj.type.value,
        payload=obj.payload,
        confidence=obj.confidence,
        importance=obj.importance,
        source_action_id=obj.source_action_id,
        source_conversation_id=obj.source_conversation_id,
        source_message_id=obj.source_message_id,
        valid_from=obj.valid_from,
        valid_to=obj.valid_to,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=KnowledgeListResponse)
async def list_knowledge_objects(
    user: CurrentUser,
    type: list[str] | None = Query(
        default=None,
        description="Filter by type(s): taxonomy_label, breakdown, insight, goal, plan, habit, etc.",
    ),
    from_date: datetime | None = Query(
        default=None,
        description="Filter objects created after this date",
    ),
    to_date: datetime | None = Query(
        default=None,
        description="Filter objects created before this date",
    ),
    include_expired: bool = Query(
        default=False,
        description="Include objects past their valid_to date",
    ),
    limit: int = Query(default=50, ge=1, le=100, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    service: KnowledgeObjectService = Depends(get_knowledge_object_service),
) -> KnowledgeListResponse:
    """Query knowledge objects with filters.

    Returns paginated list of knowledge objects for the authenticated user.
    Supports filtering by type, date range, and expiry status.
    """
    logger.info(
        "Querying knowledge objects",
        user_id=user.id,
        types=type,
        limit=limit,
        offset=offset,
    )

    # Convert type strings to enum
    types = None
    if type:
        try:
            types = [KnowledgeObjectType(t) for t in type]
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type: {str(e)}. Valid types: {[t.value for t in KnowledgeObjectType]}",
            )

    query = KnowledgeObjectQuery(
        types=types,
        from_date=from_date,
        to_date=to_date,
        include_expired=include_expired,
        limit=limit,
        offset=offset,
    )

    result = await service.query(user.id, query)

    return KnowledgeListResponse(
        objects=[_to_response(obj) for obj in result.objects],
        total=result.total,
        has_more=result.has_more,
        cursor=str(offset + limit) if result.has_more else None,
    )


@router.get("/by-action/{action_id}", response_model=KnowledgeListResponse)
async def get_knowledge_by_action(
    action_id: str,
    user: CurrentUser,
    type: list[str] | None = Query(
        default=None,
        description="Filter by type(s)",
    ),
    service: KnowledgeObjectService = Depends(get_knowledge_object_service),
) -> KnowledgeListResponse:
    """Get all knowledge objects associated with an action.

    Returns taxonomy labels, breakdowns, and other knowledge linked
    to the specified action.
    """
    logger.info(
        "Getting knowledge for action",
        user_id=user.id,
        action_id=action_id,
    )

    types = None
    if type:
        try:
            types = [KnowledgeObjectType(t) for t in type]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid type: {str(e)}")

    objects = await service.get_by_action(user.id, action_id, types)

    return KnowledgeListResponse(
        objects=[_to_response(obj) for obj in objects],
        total=len(objects),
        has_more=False,
    )


@router.get("/by-conversation/{conversation_id}", response_model=KnowledgeListResponse)
async def get_knowledge_by_conversation(
    conversation_id: str,
    user: CurrentUser,
    type: list[str] | None = Query(
        default=None,
        description="Filter by type(s)",
    ),
    service: KnowledgeObjectService = Depends(get_knowledge_object_service),
) -> KnowledgeListResponse:
    """Get all knowledge objects associated with a conversation.

    Returns checkpoints, insights, and other knowledge linked
    to the specified conversation.
    """
    logger.info(
        "Getting knowledge for conversation",
        user_id=user.id,
        conversation_id=conversation_id,
    )

    types = None
    if type:
        try:
            types = [KnowledgeObjectType(t) for t in type]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid type: {str(e)}")

    query = KnowledgeObjectQuery(
        types=types,
        source_conversation_id=conversation_id,
        limit=100,
    )
    result = await service.query(user.id, query)

    return KnowledgeListResponse(
        objects=[_to_response(obj) for obj in result.objects],
        total=result.total,
        has_more=result.has_more,
    )


@router.get("/search", response_model=KnowledgeListResponse)
async def search_knowledge(
    user: CurrentUser,
    q: str = Query(..., min_length=2, description="Search query"),
    type: list[str] | None = Query(
        default=None,
        description="Filter by type(s)",
    ),
    limit: int = Query(default=20, ge=1, le=50, description="Max results"),
    service: KnowledgeObjectService = Depends(get_knowledge_object_service),
) -> KnowledgeListResponse:
    """Search knowledge objects by payload content.

    Performs basic text search within the JSONB payload.
    For complex queries, consider using the filter endpoints.
    """
    logger.info(
        "Searching knowledge objects",
        user_id=user.id,
        query=q,
        limit=limit,
    )

    types = None
    if type:
        try:
            types = [KnowledgeObjectType(t) for t in type]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid type: {str(e)}")

    objects = await service.search_payload(user.id, q, types, limit)

    return KnowledgeListResponse(
        objects=[_to_response(obj) for obj in objects],
        total=len(objects),
        has_more=False,  # Search doesn't paginate
    )


@router.get("/latest-state", response_model=LatestStateResponse)
async def get_latest_state(
    user: CurrentUser,
    service: KnowledgeObjectService = Depends(get_knowledge_object_service),
) -> LatestStateResponse:
    """Get the latest derived state for the user.

    Returns active goals, plans, habits, and recent insights.
    Useful for building a dashboard or understanding current focus areas.
    """
    logger.info("Getting latest state", user_id=user.id)

    # Fetch different types in parallel conceptually (sequential for simplicity)
    goals = await service.get_by_type(user.id, KnowledgeObjectType.GOAL, limit=10)
    plans = await service.get_by_type(user.id, KnowledgeObjectType.PLAN, limit=10)
    habits = await service.get_by_type(user.id, KnowledgeObjectType.HABIT, limit=10)
    insights = await service.get_latest_insights(user.id, limit=5)

    # Get total count
    all_query = KnowledgeObjectQuery(limit=1)
    all_result = await service.query(user.id, all_query)

    return LatestStateResponse(
        goals=[_to_response(obj) for obj in goals],
        plans=[_to_response(obj) for obj in plans],
        habits=[_to_response(obj) for obj in habits],
        recent_insights=[_to_response(obj) for obj in insights],
        total_knowledge_objects=all_result.total,
    )


@router.get("/{object_id}", response_model=KnowledgeObjectResponse)
async def get_knowledge_object(
    object_id: str,
    user: CurrentUser,
    service: KnowledgeObjectService = Depends(get_knowledge_object_service),
) -> KnowledgeObjectResponse:
    """Get a specific knowledge object by ID."""
    logger.info(
        "Getting knowledge object",
        user_id=user.id,
        object_id=object_id,
    )

    obj = await service.get_by_id(user.id, object_id)

    if not obj:
        raise HTTPException(status_code=404, detail="Knowledge object not found")

    return _to_response(obj)


@router.delete("/{object_id}")
async def delete_knowledge_object(
    object_id: str,
    user: CurrentUser,
    service: KnowledgeObjectService = Depends(get_knowledge_object_service),
) -> dict[str, bool]:
    """Delete a knowledge object."""
    logger.info(
        "Deleting knowledge object",
        user_id=user.id,
        object_id=object_id,
    )

    success = await service.delete(user.id, object_id)

    if not success:
        raise HTTPException(status_code=404, detail="Knowledge object not found or already deleted")

    return {"success": True}


@router.post("/{object_id}/expire")
async def expire_knowledge_object(
    object_id: str,
    user: CurrentUser,
    service: KnowledgeObjectService = Depends(get_knowledge_object_service),
) -> dict[str, bool]:
    """Mark a knowledge object as expired.

    Sets valid_to to now, making it excluded from default queries.
    The object is not deleted and can still be retrieved with include_expired=true.
    """
    logger.info(
        "Expiring knowledge object",
        user_id=user.id,
        object_id=object_id,
    )

    success = await service.expire(user.id, object_id)

    if not success:
        raise HTTPException(status_code=404, detail="Knowledge object not found")

    return {"success": True}


# =============================================================================
# Types Endpoint (for discoverability)
# =============================================================================


@router.get("/meta/types")
async def get_knowledge_types() -> dict[str, list[str]]:
    """Get available knowledge object types.

    Returns the list of valid type values for filtering.
    """
    return {
        "types": [t.value for t in KnowledgeObjectType],
    }
