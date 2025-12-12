"""AI Orchestrator Router.

Main router for all AI-related endpoints including chat, extraction, and processing.
All endpoints require authentication via Supabase JWT.
"""

import json
from collections.abc import AsyncIterator
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import structlog

from app.ai import AIProvider, Message as AIMessage, get_ai_provider
from app.auth import CurrentUser, User
from app.clients.claude import ClaudeClient, get_claude_client
from app.middleware.error_handler import RateLimitError
from app.utils.rate_limiter import RateLimiter, RateLimitResult, get_rate_limiter

logger = structlog.get_logger()


# ============================================================================
# Request/Response Models
# ============================================================================


class Message(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    messages: list[Message] = Field(..., min_length=1)
    system: str | None = Field(None, description="Optional system prompt override")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    content: str = Field(..., description="Assistant response")
    input_tokens: int = Field(..., description="Tokens used in input")
    output_tokens: int = Field(..., description="Tokens used in output")


class ExtractRequest(BaseModel):
    """Request body for extraction endpoint."""

    text: str = Field(..., min_length=1, description="Text to extract from")


class ExtractResponse(BaseModel):
    """Response from extraction endpoint."""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/api/ai", tags=["ai"])


# ============================================================================
# Dependencies
# ============================================================================


def get_claude() -> ClaudeClient:
    """Dependency for Claude client."""
    return get_claude_client()


class RateLimitDep:
    """Dependency that checks rate limits for AI endpoints."""

    def __init__(self, limiter: RateLimiter = Depends(get_rate_limiter)):
        self.limiter = limiter

    def check(self, user: User) -> RateLimitResult:
        """Check if user is within rate limits."""
        return self.limiter.check(user.id)


async def check_rate_limit(
    user: CurrentUser,
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> RateLimitResult:
    """Dependency to check rate limits. Raises 429 if exceeded."""
    result = limiter.check(user.id)

    if not result.allowed:
        raise RateLimitError(
            retry_after=result.retry_after_seconds or 60,
            limit_type=result.limit_type or "minute",
        )

    return result


# Type alias for rate limit dependency
RateLimit = Annotated[RateLimitResult, Depends(check_rate_limit)]


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: CurrentUser,
    rate_limit: RateLimit,
    claude: ClaudeClient = Depends(get_claude),
) -> ChatResponse:
    """Process a chat message through Claude.

    Requires authentication. Returns the assistant's response along with
    token usage information.
    """
    logger.info(
        "Processing chat request",
        user_id=user.id,
        message_count=len(request.messages),
    )

    # Convert Pydantic models to dicts for Claude client
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    # For now, return basic response - full implementation in AGT-006 (SSE Streaming)
    response = claude.chat(
        messages=messages,
        system=request.system,
    )

    # Token counting will be enhanced in AGT-005 (Token Budgeting)
    return ChatResponse(
        content=response,
        input_tokens=0,  # Placeholder until token tracking implemented
        output_tokens=0,
    )


@router.post("/extract", response_model=ExtractResponse)
async def extract(
    request: ExtractRequest,
    user: CurrentUser,
    rate_limit: RateLimit,
) -> ExtractResponse:
    """Extract structured data from text.

    This is a placeholder endpoint. Full implementation will be added in:
    - AGT-008: Extract Actions
    - AGT-016: Extraction Orchestrator
    """
    logger.info(
        "Extraction request received",
        user_id=user.id,
        text_length=len(request.text),
    )

    # Placeholder response - actual extraction logic will be implemented
    # in AGT-008, AGT-009, AGT-010, AGT-011, and orchestrated by AGT-016
    return ExtractResponse(
        success=True,
        data={"message": "Extraction not yet implemented"},
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user: CurrentUser,
    rate_limit: RateLimit,
) -> EventSourceResponse:
    """Stream a chat response using Server-Sent Events.

    Requires authentication. Streams the assistant's response as it's generated.

    SSE Event Types:
    - message: Text chunk from the AI
    - done: Stream complete
    - error: An error occurred
    """
    logger.info(
        "Processing streaming chat request",
        user_id=user.id,
        message_count=len(request.messages),
    )

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        """Generate SSE events from Claude stream."""
        try:
            ai = get_ai_provider()

            # Convert request messages to AI provider format
            messages = [
                AIMessage(role=m.role, content=m.content)
                for m in request.messages
            ]

            # Stream the response
            async for chunk in ai.stream(
                messages=messages,
                system=request.system,
            ):
                yield {
                    "event": "message",
                    "data": json.dumps({"content": chunk}),
                }

            # Signal completion
            yield {"event": "done", "data": "{}"}

        except Exception as e:
            logger.error("Stream error", error=str(e), user_id=user.id)
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())


@router.get("/status")
async def status(
    user: CurrentUser,
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> dict[str, Any]:
    """Check AI service status.

    Returns current status of AI services for the authenticated user.
    """
    rate_status = limiter.get_status(user.id)

    return {
        "user_id": user.id,
        "services": {
            "claude": "available",
            "extraction": "available",
            "streaming": "available",
        },
        "rate_limit": {
            "minute": {
                "used": rate_status["minute_count"],
                "limit": rate_status["minute_limit"],
                "remaining": rate_status["minute_remaining"],
            },
            "day": {
                "used": rate_status["day_count"],
                "limit": rate_status["day_limit"],
                "remaining": rate_status["day_remaining"],
            },
        },
    }


