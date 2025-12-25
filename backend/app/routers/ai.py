"""AI Orchestrator Router.

Main router for all AI-related endpoints including chat, extraction, and processing.
All endpoints require authentication via Supabase JWT.
"""

import json
import time
from collections.abc import AsyncIterator
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import structlog

from app.ai import AIProvider, Message as AIMessage, get_ai_provider
from app.auth import CurrentUser, User
from app.clients.claude import ClaudeClient, get_claude_client
from app.middleware.error_handler import RateLimitError
from app.utils.rate_limiter import RateLimiter, RateLimitResult, get_rate_limiter
from app.services.intent import Intent
from app.services.intent_router import (
    IntentRouter,
    RouterResponse,
    get_intent_router,
)
from app.services.breakdown import (
    BreakdownService,
    BreakdownResult,
    get_breakdown_service,
)
from app.services.token_budget import (
    TokenBudgetService,
    TokenUsage,
    get_token_budget_service,
)
from app.services.intent_logger import log_intent
from app.contracts import (
    AgentOutputContract,
    get_contract_mapper,
    map_router_response_to_contract,
)

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


class ProcessRequest(BaseModel):
    """Request body for the main process endpoint."""

    text: str = Field(..., min_length=1, description="User message text")
    task_id: str | None = Field(None, description="Optional task context for coaching")
    task_title: str | None = Field(None, description="Optional task title for context")
    force_intent: Intent | None = Field(
        None, description="Force a specific intent (skip classification)"
    )


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
) -> ChatResponse:
    """Process a chat message through Claude.

    Requires authentication. Returns the assistant's response along with
    token usage information. Tracks token usage and logs the interaction.
    """
    import time

    start_time = time.time()

    logger.info(
        "Processing chat request",
        user_id=user.id,
        message_count=len(request.messages),
    )

    # Check token budget before making the call
    budget_service = get_token_budget_service()
    budget_status = await budget_service.check_budget(user.id)

    if not budget_status.has_budget:
        raise RateLimitError(
            retry_after=3600,  # Try again in an hour
            limit_type="token_budget",
        )

    if budget_status.warning:
        logger.warning(
            "User approaching token budget limit",
            user_id=user.id,
            percentage_used=budget_status.percentage_used,
        )

    # Use AIProvider for proper token tracking
    ai = get_ai_provider()
    messages = [AIMessage(role=m.role, content=m.content) for m in request.messages]

    response = await ai.complete(
        messages=messages,
        system=request.system,
    )

    # Record token usage (async, non-blocking on failure)
    await budget_service.record_usage(
        user_id=user.id,
        usage=TokenUsage(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            endpoint="/api/ai/chat",
        ),
    )

    # Log the intent (async, non-blocking on failure)
    processing_time_ms = int((time.time() - start_time) * 1000)
    await log_intent(
        user_id=user.id,
        raw_input=request.messages[-1].content if request.messages else "",
        classified_intent="chat",
        ai_response=response.content,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        processing_time_ms=processing_time_ms,
    )

    return ChatResponse(
        content=response.content,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
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


# ============================================================================
# Intent-Based Process Endpoints (AGT-002)
# ============================================================================


@router.post("/process")
async def process(
    request: ProcessRequest,
    user: CurrentUser,
    rate_limit: RateLimit,
    intent_router: IntentRouter = Depends(get_intent_router),
    use_contract: bool = Query(
        default=False,
        description="Return AgentOutputContract v0 format instead of RouterResponse",
    ),
) -> RouterResponse | AgentOutputContract:
    """Process a message through the intent router.

    This is the main entry point for user messages. It:
    1. Classifies the intent (CAPTURE, COACHING, or COMMAND)
    2. Routes to the appropriate handler
    3. Returns a unified response

    Intent Types:
    - CAPTURE: Task capture and extraction (e.g., "Buy milk and call mom")
    - COACHING: Emotional support (e.g., "I can't focus today")
    - COMMAND: System commands (e.g., "/help")

    You can force a specific intent using the force_intent field to skip
    classification. This is useful for UI flows where the intent is known.

    Set use_contract=true to receive the new AgentOutputContract v0 format.
    """
    start_time = time.time()

    logger.info(
        "Processing message",
        user_id=user.id,
        text_length=len(request.text),
        force_intent=request.force_intent,
        use_contract=use_contract,
    )

    if request.force_intent:
        # Skip classification, use forced intent
        response = await intent_router.route_with_intent(
            text=request.text,
            intent=request.force_intent,
            user_id=user.id,
            task_id=request.task_id,
            task_title=request.task_title,
        )
    else:
        # Normal flow: classify and route
        response = await intent_router.route(
            text=request.text,
            user_id=user.id,
            task_id=request.task_id,
            task_title=request.task_title,
        )

    # Log intent for analytics
    processing_time_ms = int((time.time() - start_time) * 1000)
    await log_intent(
        user_id=user.id,
        raw_input=request.text,
        classified_intent=response.intent.value,
        extraction_result=response.extraction.model_dump() if response.extraction else None,
        ai_response=response.coaching_response or (response.command_response.message if response.command_response else None),
        processing_time_ms=processing_time_ms,
    )

    # Return contract format if requested
    if use_contract:
        contract = map_router_response_to_contract(
            response=response,
            raw_input=request.text,
            processing_time_ms=processing_time_ms,
        )
        return contract

    return response


@router.post("/process/v2", response_model=AgentOutputContract)
async def process_v2(
    request: ProcessRequest,
    user: CurrentUser,
    rate_limit: RateLimit,
    intent_router: IntentRouter = Depends(get_intent_router),
) -> AgentOutputContract:
    """Process a message and return AgentOutputContract v0.

    This endpoint always returns the new contract format. Use this for
    new integrations or when migrating to the v0 contract.

    The contract provides:
    - Standardized response structure across all intent types
    - Rich metadata (taxonomy, magnitude, state inference)
    - UI rendering hints
    - Provenance tracking (model, prompt versions, timing)

    See /docs/contracts/agent_output_v0.md for full documentation.
    """
    start_time = time.time()

    logger.info(
        "Processing message (v2 contract)",
        user_id=user.id,
        text_length=len(request.text),
        force_intent=request.force_intent,
    )

    if request.force_intent:
        response = await intent_router.route_with_intent(
            text=request.text,
            intent=request.force_intent,
            user_id=user.id,
            task_id=request.task_id,
            task_title=request.task_title,
        )
    else:
        response = await intent_router.route(
            text=request.text,
            user_id=user.id,
            task_id=request.task_id,
            task_title=request.task_title,
        )

    processing_time_ms = int((time.time() - start_time) * 1000)

    # Log intent with contract format
    contract = map_router_response_to_contract(
        response=response,
        raw_input=request.text,
        processing_time_ms=processing_time_ms,
    )

    await log_intent(
        user_id=user.id,
        raw_input=request.text,
        classified_intent=response.intent.value,
        extraction_result=contract.model_dump(),  # Store full contract
        ai_response=response.coaching_response or (response.command_response.message if response.command_response else None),
        processing_time_ms=processing_time_ms,
    )

    return contract


@router.post("/process/stream")
async def process_stream(
    request: ProcessRequest,
    user: CurrentUser,
    rate_limit: RateLimit,
    intent_router: IntentRouter = Depends(get_intent_router),
) -> EventSourceResponse:
    """Stream a response using Server-Sent Events.

    Currently only supports COACHING intent for streaming responses.
    Other intents return their results as a single 'result' event.

    SSE Event Types:
    - message: Text chunk from coaching (streaming)
    - result: Full result JSON for non-streaming intents
    - done: Stream complete
    - error: An error occurred
    """
    logger.info(
        "Processing streaming message",
        user_id=user.id,
        text_length=len(request.text),
    )

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        """Generate SSE events based on intent."""
        try:
            # Determine intent
            if request.force_intent:
                intent = request.force_intent
            else:
                intent_result = await intent_router.classifier.classify(request.text)
                intent = intent_result.intent

            # Streaming is only for coaching
            if intent == Intent.COACHING:
                # Stream coaching response
                async for chunk in intent_router.stream_coaching(
                    text=request.text,
                    user_id=user.id,
                    task_id=request.task_id,
                    task_title=request.task_title,
                ):
                    yield {
                        "event": "message",
                        "data": json.dumps({"content": chunk}),
                    }
            else:
                # Non-streaming: process and return result
                if request.force_intent:
                    result = await intent_router.route_with_intent(
                        text=request.text,
                        intent=intent,
                        user_id=user.id,
                        task_id=request.task_id,
                        task_title=request.task_title,
                    )
                else:
                    result = await intent_router.route(
                        text=request.text,
                        user_id=user.id,
                        task_id=request.task_id,
                        task_title=request.task_title,
                    )

                yield {
                    "event": "result",
                    "data": result.model_dump_json(),
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


# ============================================================================
# Breakdown Endpoint (EXE-006)
# ============================================================================


class BreakdownRequest(BaseModel):
    """Request body for breakdown endpoint."""

    task_title: str = Field(..., min_length=1, description="Task title to break down")


@router.post("/breakdown", response_model=BreakdownResult)
async def breakdown(
    request: BreakdownRequest,
    user: CurrentUser,
    rate_limit: RateLimit,
    breakdown_service: BreakdownService = Depends(get_breakdown_service),
) -> BreakdownResult:
    """Break down a complex task into micro-steps.

    Returns 3-5 suggested first steps that are:
    - PHYSICAL: involve body movement, not just thinking
    - IMMEDIATE: can start right now
    - TINY: each takes 2-10 minutes max

    Used by EXE-006 First Step Suggestions to help users start
    overwhelming tasks.
    """
    logger.info(
        "Breaking down task",
        user_id=user.id,
        task_title=request.task_title[:50],
    )

    result = await breakdown_service.breakdown(request.task_title)

    logger.info(
        "Breakdown complete",
        user_id=user.id,
        step_count=len(result.steps),
    )

    return result
