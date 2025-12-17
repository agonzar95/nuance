"""Telegram webhook and connection router.

Handles incoming Telegram updates via webhook and user account linking.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
import structlog

from app.auth import CurrentUser
from app.clients.supabase import get_client
from app.config import settings
from app.services.telegram_connection import get_telegram_connection_service

logger = structlog.get_logger()

router = APIRouter(prefix="/telegram", tags=["telegram"])


# Request/Response models for connection endpoints
class ConnectRequest(BaseModel):
    """Request body for connecting Telegram account."""
    token: str


class ConnectResponse(BaseModel):
    """Response for Telegram connection operations."""
    success: bool
    message: str


class ConnectionStatus(BaseModel):
    """Response for connection status check."""
    connected: bool
    chat_id: str | None = None


@router.post("/connect", response_model=ConnectResponse)
async def connect_telegram(
    request: ConnectRequest,
    user: CurrentUser,
) -> ConnectResponse:
    """Connect a Telegram account to the authenticated user's profile.

    Validates the connection token from the Telegram /start command
    and links the Telegram chat ID to the user's profile.

    Args:
        request: Request body containing the connection token.
        user: Authenticated user from JWT.

    Returns:
        Success response with message.

    Raises:
        HTTPException: 400 if token is invalid or expired.
    """
    service = get_telegram_connection_service()

    # Consume the token (validates and deletes in one operation)
    chat_id = await service.consume_token(request.token)

    if chat_id is None:
        logger.warning(
            "Invalid or expired Telegram connection token",
            user_id=user.id,
            token=request.token[:8] + "..." if len(request.token) > 8 else request.token,
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token. Please send /start to the bot again.",
        )

    # Update user's profile with the Telegram chat ID
    client = get_client()
    try:
        client.table("profiles").update({
            "telegram_chat_id": chat_id
        }).eq("id", user.id).execute()

        logger.info(
            "Telegram account connected",
            user_id=user.id,
            chat_id=chat_id,
        )

        return ConnectResponse(
            success=True,
            message="Telegram account connected successfully!",
        )

    except Exception as e:
        logger.error(
            "Failed to update profile with Telegram chat ID",
            user_id=user.id,
            chat_id=chat_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to connect Telegram account. Please try again.",
        )


@router.post("/disconnect", response_model=ConnectResponse)
async def disconnect_telegram(user: CurrentUser) -> ConnectResponse:
    """Disconnect Telegram from the authenticated user's profile.

    Clears the telegram_chat_id from the user's profile.

    Args:
        user: Authenticated user from JWT.

    Returns:
        Success response with message.
    """
    client = get_client()

    try:
        # Clear the telegram_chat_id from profile
        client.table("profiles").update({
            "telegram_chat_id": None
        }).eq("id", user.id).execute()

        logger.info(
            "Telegram account disconnected",
            user_id=user.id,
        )

        return ConnectResponse(
            success=True,
            message="Telegram account disconnected.",
        )

    except Exception as e:
        logger.error(
            "Failed to disconnect Telegram account",
            user_id=user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to disconnect Telegram account. Please try again.",
        )


@router.get("/status", response_model=ConnectionStatus)
async def get_telegram_status(user: CurrentUser) -> ConnectionStatus:
    """Get the Telegram connection status for the authenticated user.

    Args:
        user: Authenticated user from JWT.

    Returns:
        Connection status with chat ID if connected.
    """
    client = get_client()

    try:
        result = client.table("profiles").select(
            "telegram_chat_id"
        ).eq("id", user.id).execute()

        if result.data:
            row = result.data[0]
            if isinstance(row, dict):
                chat_id = row.get("telegram_chat_id")
                if chat_id and isinstance(chat_id, str):
                    return ConnectionStatus(
                        connected=True,
                        chat_id=chat_id,
                    )

        return ConnectionStatus(connected=False)

    except Exception as e:
        logger.error(
            "Failed to get Telegram status",
            user_id=user.id,
            error=str(e),
        )
        return ConnectionStatus(connected=False)


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, bool]:
    """Receive Telegram webhook updates.

    This endpoint receives updates from Telegram when users interact
    with the bot. The secret token header is verified if configured.

    Args:
        request: FastAPI request with update payload.
        x_telegram_bot_api_secret_token: Secret token from Telegram.

    Returns:
        Success response.

    Raises:
        HTTPException: 401 if secret token is invalid, 500 on processing error.
    """
    # Verify secret token if configured
    expected_secret = settings.telegram_webhook_secret or settings.telegram_secret_token
    if expected_secret:
        if x_telegram_bot_api_secret_token != expected_secret:
            logger.warning("Invalid webhook secret token")
            raise HTTPException(status_code=401, detail="Invalid secret token")

    try:
        update: dict[str, Any] = await request.json()
        logger.debug("Received Telegram update", update_id=update.get("update_id"))

        # Process the update (handler will be implemented in NTF-005)
        await process_telegram_update(update)

        return {"ok": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Webhook processing error", error=str(e))
        # Return 200 to prevent Telegram from retrying
        # Log the error for debugging
        return {"ok": True}


async def process_telegram_update(update: dict[str, Any]) -> None:
    """Process incoming Telegram update.

    Routes the update to the appropriate handler for processing.

    Args:
        update: Raw Telegram update payload.
    """
    try:
        from app.services.notifications.telegram import get_telegram_handler

        handler = get_telegram_handler()
        await handler.process_update(update)

    except Exception as e:
        logger.error(
            "Failed to process Telegram update",
            update_id=update.get("update_id"),
            error=str(e),
        )


@router.get("/webhook/info")
async def webhook_info() -> dict[str, Any]:
    """Get current webhook configuration status.

    Returns:
        Webhook information from Telegram API.
    """
    try:
        from app.services.notifications.telegram import get_bot_setup

        setup = get_bot_setup()
        info = await setup.get_webhook_info()
        await setup.close()

        if info:
            return {
                "url": info.url,
                "pending_update_count": info.pending_update_count,
                "last_error_date": info.last_error_date,
                "last_error_message": info.last_error_message,
                "max_connections": info.max_connections,
                "allowed_updates": info.allowed_updates,
            }
        return {"error": "Failed to get webhook info"}

    except Exception as e:
        logger.error("Failed to get webhook info", error=str(e))
        return {"error": str(e)}


@router.post("/webhook/setup")
async def setup_webhook() -> dict[str, Any]:
    """Set up webhook for receiving Telegram updates.

    This endpoint should only be called during deployment or
    when webhook configuration needs to change.

    Returns:
        Success status.
    """
    try:
        from app.services.notifications.telegram import get_bot_setup

        setup = get_bot_setup()

        # Verify bot first
        bot_info = await setup.verify_bot()
        if not bot_info:
            await setup.close()
            return {"success": False, "error": "Bot verification failed"}

        # Set up webhook
        success = await setup.setup_webhook()
        await setup.close()

        if success:
            return {
                "success": True,
                "bot": {
                    "id": bot_info.id,
                    "username": bot_info.username,
                },
            }
        return {"success": False, "error": "Webhook setup failed"}

    except Exception as e:
        logger.error("Webhook setup error", error=str(e))
        return {"success": False, "error": str(e)}


@router.delete("/webhook")
async def delete_webhook(drop_pending: bool = False) -> dict[str, Any]:
    """Remove webhook (for switching to polling mode).

    Args:
        drop_pending: Whether to drop pending updates.

    Returns:
        Success status.
    """
    try:
        from app.services.notifications.telegram import get_bot_setup

        setup = get_bot_setup()
        success = await setup.delete_webhook(drop_pending_updates=drop_pending)
        await setup.close()

        return {"success": success}

    except Exception as e:
        logger.error("Webhook delete error", error=str(e))
        return {"success": False, "error": str(e)}


@router.get("/bot/verify")
async def verify_bot() -> dict[str, Any]:
    """Verify bot token and get bot info.

    Returns:
        Bot information if token is valid.
    """
    try:
        from app.services.notifications.telegram import get_bot_setup

        setup = get_bot_setup()
        bot_info = await setup.verify_bot()
        await setup.close()

        if bot_info:
            return {
                "valid": True,
                "bot": {
                    "id": bot_info.id,
                    "username": bot_info.username,
                    "first_name": bot_info.first_name,
                    "can_join_groups": bot_info.can_join_groups,
                    "supports_inline_queries": bot_info.supports_inline_queries,
                },
            }
        return {"valid": False, "error": "Bot verification failed"}

    except ValueError as e:
        return {"valid": False, "error": str(e)}
    except Exception as e:
        logger.error("Bot verification error", error=str(e))
        return {"valid": False, "error": str(e)}
