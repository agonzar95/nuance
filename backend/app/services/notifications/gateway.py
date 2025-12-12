"""Notification gateway.

Unified interface for sending notifications through any channel.
Routes to the appropriate provider based on user preferences.
"""

import structlog

from app.services.notifications.base import (
    NotificationChannel,
    NotificationPayload,
    DeliveryResult,
    NotificationProvider,
)
from app.services.notifications.router import (
    ChannelRouter,
    get_channel_router,
)
from app.services.notifications.providers import (
    EmailProvider,
    TelegramNotificationProvider,
    get_email_provider,
    get_telegram_provider,
)

logger = structlog.get_logger()


class NotificationGateway:
    """Unified notification gateway.

    Provides a single interface for sending notifications through
    any channel. Routes to the appropriate provider based on user
    preferences and channel availability.

    Example:
        gateway = NotificationGateway()
        result = await gateway.send(NotificationPayload(
            user_id="user_123",
            notification_type=NotificationType.MORNING_PLAN,
            subject="Your plan for today",
            body="Here are your priorities...",
            data={"tasks": [...]}
        ))
    """

    def __init__(
        self,
        email_provider: NotificationProvider | None = None,
        telegram_provider: NotificationProvider | None = None,
        router: ChannelRouter | None = None,
    ):
        """Initialize the gateway.

        Args:
            email_provider: Email provider instance.
            telegram_provider: Telegram provider instance.
            router: Channel router instance.
        """
        self._providers: dict[NotificationChannel, NotificationProvider] = {}

        # Register providers
        if email_provider:
            self._providers[NotificationChannel.EMAIL] = email_provider
        if telegram_provider:
            self._providers[NotificationChannel.TELEGRAM] = telegram_provider

        self._router = router or get_channel_router()

    def register_provider(
        self,
        channel: NotificationChannel,
        provider: NotificationProvider,
    ) -> None:
        """Register a provider for a channel.

        Args:
            channel: Channel to register.
            provider: Provider instance.
        """
        self._providers[channel] = provider

    async def send(
        self,
        payload: NotificationPayload,
        channel: NotificationChannel | None = None,
    ) -> DeliveryResult:
        """Send a notification to a user.

        Routes to the user's preferred channel unless a specific
        channel is requested.

        Args:
            payload: Notification content and metadata.
            channel: Optional specific channel to use.

        Returns:
            DeliveryResult indicating success or failure.
        """
        # Determine which channel to use
        if channel is None:
            channel = await self._router.get_channel(
                payload.user_id,
                payload.notification_type,
            )

        if channel is None:
            logger.warning(
                "No channel available for user",
                user_id=payload.user_id,
                notification_type=payload.notification_type.value,
            )
            return DeliveryResult(
                success=False,
                channel=NotificationChannel.EMAIL,  # Default for reporting
                error="No notification channel available for user",
            )

        # Get provider for channel
        provider = self._providers.get(channel)
        if provider is None:
            logger.error(
                "No provider registered for channel",
                channel=channel.value,
            )
            return DeliveryResult(
                success=False,
                channel=channel,
                error=f"No provider registered for channel: {channel.value}",
            )

        # Send notification
        try:
            result = await provider.send(payload.user_id, payload)

            logger.info(
                "Notification sent",
                user_id=payload.user_id,
                notification_type=payload.notification_type.value,
                channel=channel.value,
                success=result.success,
                provider_id=result.provider_id,
            )

            return result

        except Exception as e:
            logger.error(
                "Notification send failed",
                user_id=payload.user_id,
                channel=channel.value,
                error=str(e),
            )
            return DeliveryResult(
                success=False,
                channel=channel,
                error=str(e),
            )

    async def send_to_channel(
        self,
        payload: NotificationPayload,
        channel: NotificationChannel,
    ) -> DeliveryResult:
        """Send notification to a specific channel.

        Use this when you need to ensure delivery to a specific
        channel, bypassing routing.

        Args:
            payload: Notification content.
            channel: Channel to use.

        Returns:
            DeliveryResult indicating success or failure.
        """
        return await self.send(payload, channel=channel)

    async def send_to_all(
        self,
        payload: NotificationPayload,
    ) -> list[DeliveryResult]:
        """Send notification to all available channels.

        Useful for high-priority notifications that should
        reach the user through all means.

        Args:
            payload: Notification content.

        Returns:
            List of DeliveryResults for each channel attempted.
        """
        results: list[DeliveryResult] = []

        available_channels = await self._router.get_available_channels(
            payload.user_id
        )

        for channel in available_channels:
            result = await self.send(payload, channel=channel)
            results.append(result)

        return results

    async def is_configured(self, user_id: str) -> bool:
        """Check if user has any notification channel configured.

        Args:
            user_id: User to check.

        Returns:
            True if at least one channel is available.
        """
        channels = await self._router.get_available_channels(user_id)
        return len(channels) > 0

    async def get_available_channels(
        self,
        user_id: str,
    ) -> list[NotificationChannel]:
        """Get list of available channels for a user.

        Args:
            user_id: User to check.

        Returns:
            List of available notification channels.
        """
        return await self._router.get_available_channels(user_id)


def get_notification_gateway() -> NotificationGateway:
    """Factory function for dependency injection.

    Returns:
        Configured NotificationGateway with all providers.
    """
    try:
        email_provider = get_email_provider()
    except Exception as e:
        logger.warning("Email provider not available", error=str(e))
        email_provider = None

    try:
        telegram_provider = get_telegram_provider()
    except Exception as e:
        logger.warning("Telegram provider not available", error=str(e))
        telegram_provider = None

    return NotificationGateway(
        email_provider=email_provider,
        telegram_provider=telegram_provider,
    )
