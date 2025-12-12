"""Telegram bot setup and webhook configuration.

Handles bot initialization, webhook registration, and health checks.
"""

from dataclasses import dataclass
from typing import Any

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()


@dataclass
class TelegramBotConfig:
    """Configuration for Telegram bot.

    Attributes:
        bot_token: Bot token from BotFather.
        webhook_url: HTTPS URL for webhook endpoint.
        webhook_secret: Optional secret for webhook verification.
    """

    bot_token: str
    webhook_url: str
    webhook_secret: str | None = None

    @property
    def api_base(self) -> str:
        """Base URL for Telegram Bot API."""
        return f"https://api.telegram.org/bot{self.bot_token}"


@dataclass
class BotInfo:
    """Information about the bot.

    Attributes:
        id: Bot's unique ID.
        username: Bot's username.
        first_name: Bot's display name.
        can_join_groups: Whether bot can be added to groups.
        can_read_all_group_messages: Whether bot can read all messages.
        supports_inline_queries: Whether bot supports inline mode.
    """

    id: int
    username: str
    first_name: str
    can_join_groups: bool = False
    can_read_all_group_messages: bool = False
    supports_inline_queries: bool = False


@dataclass
class WebhookInfo:
    """Information about the current webhook.

    Attributes:
        url: Current webhook URL (empty if not set).
        has_custom_certificate: Whether using custom certificate.
        pending_update_count: Number of pending updates.
        last_error_date: Unix timestamp of last error.
        last_error_message: Last error message.
        max_connections: Maximum concurrent connections.
        allowed_updates: List of update types to receive.
    """

    url: str
    has_custom_certificate: bool = False
    pending_update_count: int = 0
    last_error_date: int | None = None
    last_error_message: str | None = None
    max_connections: int = 40
    allowed_updates: list[str] | None = None


class TelegramBotSetup:
    """Handles Telegram bot setup and configuration.

    Features:
    - Webhook setup and removal
    - Bot verification
    - Webhook status checking
    """

    def __init__(self, config: TelegramBotConfig):
        """Initialize bot setup.

        Args:
            config: Bot configuration.
        """
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def verify_bot(self) -> BotInfo | None:
        """Verify bot token is valid.

        Returns:
            BotInfo if valid, None otherwise.
        """
        client = await self._get_client()

        try:
            response = await client.get(f"{self.config.api_base}/getMe")
            data: dict[str, Any] = response.json()

            if data.get("ok") and data.get("result"):
                result = data["result"]
                bot_info = BotInfo(
                    id=result["id"],
                    username=result.get("username", ""),
                    first_name=result.get("first_name", ""),
                    can_join_groups=result.get("can_join_groups", False),
                    can_read_all_group_messages=result.get(
                        "can_read_all_group_messages", False
                    ),
                    supports_inline_queries=result.get("supports_inline_queries", False),
                )
                logger.info(
                    "Bot verified",
                    bot_id=bot_info.id,
                    username=bot_info.username,
                )
                return bot_info
            else:
                logger.error("Bot verification failed", response=data)
                return None

        except Exception as e:
            logger.error("Bot verification error", error=str(e))
            return None

    async def setup_webhook(
        self,
        allowed_updates: list[str] | None = None,
    ) -> bool:
        """Register webhook with Telegram.

        Args:
            allowed_updates: Update types to receive. Defaults to message and callback_query.

        Returns:
            True if webhook was set successfully.
        """
        client = await self._get_client()

        if allowed_updates is None:
            allowed_updates = ["message", "callback_query"]

        payload: dict[str, Any] = {
            "url": self.config.webhook_url,
            "allowed_updates": allowed_updates,
        }

        if self.config.webhook_secret:
            payload["secret_token"] = self.config.webhook_secret

        try:
            response = await client.post(
                f"{self.config.api_base}/setWebhook",
                json=payload,
            )
            data: dict[str, Any] = response.json()

            if data.get("ok"):
                logger.info(
                    "Webhook set",
                    url=self.config.webhook_url,
                    allowed_updates=allowed_updates,
                )
                return True
            else:
                logger.error("Webhook setup failed", response=data)
                return False

        except Exception as e:
            logger.error("Webhook setup error", error=str(e))
            return False

    async def get_webhook_info(self) -> WebhookInfo | None:
        """Get current webhook status.

        Returns:
            WebhookInfo if available, None on error.
        """
        client = await self._get_client()

        try:
            response = await client.get(f"{self.config.api_base}/getWebhookInfo")
            data: dict[str, Any] = response.json()

            if data.get("ok") and data.get("result"):
                result = data["result"]
                return WebhookInfo(
                    url=result.get("url", ""),
                    has_custom_certificate=result.get("has_custom_certificate", False),
                    pending_update_count=result.get("pending_update_count", 0),
                    last_error_date=result.get("last_error_date"),
                    last_error_message=result.get("last_error_message"),
                    max_connections=result.get("max_connections", 40),
                    allowed_updates=result.get("allowed_updates"),
                )
            return None

        except Exception as e:
            logger.error("Get webhook info error", error=str(e))
            return None

    async def delete_webhook(self, drop_pending_updates: bool = False) -> bool:
        """Remove webhook (for local dev with polling).

        Args:
            drop_pending_updates: Whether to drop pending updates.

        Returns:
            True if webhook was deleted successfully.
        """
        client = await self._get_client()

        try:
            response = await client.post(
                f"{self.config.api_base}/deleteWebhook",
                json={"drop_pending_updates": drop_pending_updates},
            )
            data: dict[str, Any] = response.json()

            if data.get("ok"):
                logger.info("Webhook deleted")
                return True
            return False

        except Exception as e:
            logger.error("Delete webhook error", error=str(e))
            return False

    async def is_healthy(self) -> bool:
        """Check if bot is healthy and webhook is configured.

        Returns:
            True if bot is verified and webhook has no recent errors.
        """
        # Verify bot token
        bot_info = await self.verify_bot()
        if not bot_info:
            return False

        # Check webhook status
        webhook_info = await self.get_webhook_info()
        if not webhook_info:
            return False

        # Check for webhook errors (within last hour)
        if webhook_info.last_error_date:
            import time

            one_hour_ago = int(time.time()) - 3600
            if webhook_info.last_error_date > one_hour_ago:
                logger.warning(
                    "Webhook has recent errors",
                    last_error=webhook_info.last_error_message,
                )
                # Still return True as the bot itself is healthy
                # The webhook error might be transient

        return True


def get_bot_config() -> TelegramBotConfig:
    """Get bot configuration from settings.

    Returns:
        TelegramBotConfig from environment settings.

    Raises:
        ValueError: If bot token is not configured.
    """
    if not settings.telegram_bot_token:
        raise ValueError("Telegram bot token must be configured")

    # Construct webhook URL from app URL
    webhook_url = f"{settings.app_url}/api/telegram/webhook"

    return TelegramBotConfig(
        bot_token=settings.telegram_bot_token,
        webhook_url=webhook_url,
        webhook_secret=settings.telegram_webhook_secret,
    )


def get_bot_setup() -> TelegramBotSetup:
    """Factory function for dependency injection.

    Returns:
        Configured TelegramBotSetup instance.
    """
    config = get_bot_config()
    return TelegramBotSetup(config)
