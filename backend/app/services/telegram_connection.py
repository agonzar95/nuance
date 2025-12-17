"""Telegram connection service for account linking.

Manages temporary connection tokens that link Telegram chat IDs
to user accounts. Tokens expire after 15 minutes and are consumed
on successful account linking.
"""

import secrets
from datetime import datetime, timedelta, UTC

import structlog

from app.clients.supabase import get_client

logger = structlog.get_logger()

# Token expiration time in minutes
TOKEN_EXPIRY_MINUTES = 15


class TelegramConnectionService:
    """Service for managing Telegram account connection tokens."""

    def __init__(self) -> None:
        self._client = get_client()

    async def create_token(self, chat_id: str) -> str:
        """Generate a connection token for a Telegram chat ID.

        Creates a URL-safe token, stores it with a 15-minute expiry,
        and returns the token string.

        Args:
            chat_id: The Telegram chat ID to associate with this token.

        Returns:
            A 43-character URL-safe token string.
        """
        # Generate URL-safe token (32 bytes = 43 chars base64)
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)

        # Delete any existing tokens for this chat_id first
        self._client.table("pending_telegram_connections").delete().eq(
            "telegram_chat_id", chat_id
        ).execute()

        # Insert new token
        self._client.table("pending_telegram_connections").insert({
            "token": token,
            "telegram_chat_id": chat_id,
            "expires_at": expires_at.isoformat(),
        }).execute()

        logger.debug(
            "Created Telegram connection token",
            chat_id=chat_id,
            expires_at=expires_at.isoformat(),
        )

        return token

    async def validate_token(self, token: str) -> str | None:
        """Validate a connection token and return the associated chat ID.

        Checks if the token exists and has not expired.

        Args:
            token: The connection token to validate.

        Returns:
            The Telegram chat ID if valid, None otherwise.
        """
        result = self._client.table("pending_telegram_connections").select(
            "telegram_chat_id", "expires_at"
        ).eq("token", token).execute()

        if not result.data:
            logger.debug("Token not found", token=token[:8] + "...")
            return None

        row = result.data[0]
        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))

        if expires_at < datetime.now(UTC):
            logger.debug("Token expired", token=token[:8] + "...")
            return None

        return row["telegram_chat_id"]

    async def consume_token(self, token: str) -> str | None:
        """Validate and consume a connection token.

        If the token is valid, deletes it and returns the chat ID.
        This ensures tokens can only be used once.

        Args:
            token: The connection token to consume.

        Returns:
            The Telegram chat ID if valid, None otherwise.
        """
        # First validate the token
        chat_id = await self.validate_token(token)
        if chat_id is None:
            return None

        # Delete the token (consume it)
        self._client.table("pending_telegram_connections").delete().eq(
            "token", token
        ).execute()

        logger.info(
            "Consumed Telegram connection token",
            chat_id=chat_id,
            token=token[:8] + "...",
        )

        return chat_id

    async def cleanup_expired(self) -> int:
        """Delete all expired connection tokens.

        Returns:
            The number of tokens deleted.
        """
        now = datetime.now(UTC).isoformat()

        # Get count of expired tokens first
        result = self._client.table("pending_telegram_connections").select(
            "id", count="exact"
        ).lt("expires_at", now).execute()

        count = len(result.data) if result.data else 0

        if count > 0:
            # Delete expired tokens
            self._client.table("pending_telegram_connections").delete().lt(
                "expires_at", now
            ).execute()

            logger.info("Cleaned up expired Telegram tokens", count=count)

        return count


# Singleton instance
_service: TelegramConnectionService | None = None


def get_telegram_connection_service() -> TelegramConnectionService:
    """Get or create the singleton TelegramConnectionService."""
    global _service
    if _service is None:
        _service = TelegramConnectionService()
    return _service
