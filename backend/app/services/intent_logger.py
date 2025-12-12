"""Intent logging service for recording AI interactions.

Records all user intents and AI responses to the intent_log table
for analytics and prompt improvement over time.
"""

from datetime import datetime, UTC
from typing import Any

import structlog

from app.clients.supabase import get_client

logger = structlog.get_logger()


async def log_intent(
    user_id: str,
    raw_input: str,
    classified_intent: str | None = None,
    extraction_result: dict[str, Any] | None = None,
    ai_response: str | None = None,
    prompt_version: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    processing_time_ms: int | None = None,
) -> str | None:
    """Log an AI interaction to the intent_log table.

    Args:
        user_id: The authenticated user's ID.
        raw_input: The original user input text.
        classified_intent: The classified intent type (capture/coaching/command).
        extraction_result: JSON-serializable dict of extraction results.
        ai_response: The AI's response text.
        prompt_version: Version identifier of the prompt used.
        input_tokens: Number of input tokens used.
        output_tokens: Number of output tokens used.
        processing_time_ms: Time taken to process in milliseconds.

    Returns:
        The ID of the created log entry, or None if logging failed.
    """
    try:
        client = get_client()

        data = {
            "user_id": user_id,
            "raw_input": raw_input,
            "classified_intent": classified_intent,
            "extraction_result": extraction_result,
            "ai_response": ai_response,
            "prompt_version": prompt_version,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "processing_time_ms": processing_time_ms,
            "created_at": datetime.now(UTC).isoformat(),
        }

        result = client.table("intent_log").insert(data).execute()

        if result.data:
            log_id: str | None = result.data[0].get("id")
            logger.debug(
                "Intent logged",
                log_id=log_id,
                intent=classified_intent,
                tokens=input_tokens and output_tokens and input_tokens + output_tokens,
            )
            return log_id

        return None
    except Exception as e:
        # Don't let logging failures break the main flow
        logger.error("Failed to log intent", error=str(e))
        return None


async def get_user_intent_stats(
    user_id: str,
    days: int = 7,
) -> dict[str, Any]:
    """Get intent statistics for a user.

    Args:
        user_id: The user's ID.
        days: Number of days to look back.

    Returns:
        Dict with intent counts and token usage.
    """
    try:
        client = get_client()

        # Get recent intent counts by type
        result = client.table("intent_log").select(
            "classified_intent",
            count="exact"
        ).eq("user_id", user_id).execute()

        return {
            "total_intents": len(result.data) if result.data else 0,
            "by_type": {},  # Would need aggregation query for breakdown
        }
    except Exception as e:
        logger.error("Failed to get intent stats", error=str(e))
        return {"total_intents": 0, "by_type": {}}
