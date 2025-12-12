"""Notification channel router.

Routes notifications to the user's preferred channel based on
their preferences and channel availability.
"""

from dataclasses import dataclass

import structlog

from app.clients.supabase import get_supabase_client
from app.services.notifications.base import (
    NotificationChannel,
    NotificationType,
)

logger = structlog.get_logger()


@dataclass
class NotificationPreferences:
    """User's notification channel preferences.

    Attributes:
        default_channel: Default channel for notifications.
        email_enabled: Whether email notifications are enabled.
        telegram_enabled: Whether Telegram notifications are enabled.
    """

    default_channel: NotificationChannel
    email_enabled: bool
    telegram_enabled: bool


@dataclass
class UserChannelConfig:
    """User's channel configuration (what's available).

    Attributes:
        email: User's email address.
        telegram_chat_id: User's Telegram chat ID if connected.
    """

    email: str | None
    telegram_chat_id: str | None


class ChannelRouter:
    """Routes notifications to the appropriate channel.

    Determines which channel to use based on:
    1. User's notification preferences
    2. Notification type (some types may have specific channels)
    3. Channel availability (e.g., Telegram not connected)

    Falls back to available channels if preferred is unavailable.
    """

    def __init__(self) -> None:
        """Initialize channel router."""
        self._supabase = get_supabase_client()

    async def get_channel(
        self,
        user_id: str,
        notification_type: NotificationType,
    ) -> NotificationChannel | None:
        """Determine which channel to use for a notification.

        Args:
            user_id: User to route notification for.
            notification_type: Type of notification being sent.

        Returns:
            Channel to use, or None if no channels available.
        """
        # Get user preferences and config
        prefs = await self._get_preferences(user_id)
        config = await self._get_channel_config(user_id)

        if not prefs or not config:
            return self._get_default_channel(config)

        # Get preferred channel for this notification type
        preferred = self._get_preferred_channel(prefs, notification_type)

        # Check if preferred channel is available
        if self._is_channel_available(preferred, config, prefs):
            return preferred

        # Fall back to other available channel
        return self._get_fallback_channel(preferred, config, prefs)

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
        prefs = await self._get_preferences(user_id)
        config = await self._get_channel_config(user_id)

        available = []

        if config:
            if config.email and (not prefs or prefs.email_enabled):
                available.append(NotificationChannel.EMAIL)
            if config.telegram_chat_id and (not prefs or prefs.telegram_enabled):
                available.append(NotificationChannel.TELEGRAM)

        return available

    async def _get_preferences(self, user_id: str) -> NotificationPreferences | None:
        """Get user's notification preferences.

        Args:
            user_id: User ID.

        Returns:
            Preferences or None if not found.
        """
        try:
            response = (
                self._supabase.table("profiles")
                .select("notification_channel, notification_enabled")
                .eq("id", user_id)
                .single()
                .execute()
            )

            if response.data and isinstance(response.data, dict):
                channel_str = response.data.get("notification_channel", "email")
                enabled = response.data.get("notification_enabled", True)

                # Parse channel preference
                if channel_str == "both":
                    # "both" means both are enabled, default to email
                    return NotificationPreferences(
                        default_channel=NotificationChannel.EMAIL,
                        email_enabled=enabled,
                        telegram_enabled=enabled,
                    )
                elif channel_str == "telegram":
                    return NotificationPreferences(
                        default_channel=NotificationChannel.TELEGRAM,
                        email_enabled=False,
                        telegram_enabled=enabled,
                    )
                else:  # email
                    return NotificationPreferences(
                        default_channel=NotificationChannel.EMAIL,
                        email_enabled=enabled,
                        telegram_enabled=False,
                    )

            return None

        except Exception as e:
            logger.error("Failed to get preferences", user_id=user_id, error=str(e))
            return None

    async def _get_channel_config(self, user_id: str) -> UserChannelConfig | None:
        """Get user's channel configuration.

        Args:
            user_id: User ID.

        Returns:
            Channel config or None if not found.
        """
        try:
            # Get Telegram chat ID from profile
            profile_response = (
                self._supabase.table("profiles")
                .select("telegram_chat_id")
                .eq("id", user_id)
                .single()
                .execute()
            )

            telegram_chat_id = None
            if profile_response.data and isinstance(profile_response.data, dict):
                telegram_chat_id = profile_response.data.get("telegram_chat_id")

            # Get email from auth.users
            email = None
            try:
                user_response = self._supabase.auth.admin.get_user_by_id(user_id)
                if user_response and user_response.user:
                    email = user_response.user.email
            except Exception as e:
                logger.warning("Failed to get user email", user_id=user_id, error=str(e))

            return UserChannelConfig(
                email=email,
                telegram_chat_id=str(telegram_chat_id) if telegram_chat_id else None,
            )

        except Exception as e:
            logger.error("Failed to get channel config", user_id=user_id, error=str(e))
            return None

    def _get_preferred_channel(
        self,
        prefs: NotificationPreferences,
        notification_type: NotificationType,
    ) -> NotificationChannel:
        """Get preferred channel for notification type.

        Some notification types may have specific channel preferences,
        but for now we use the user's default.

        Args:
            prefs: User preferences.
            notification_type: Type of notification.

        Returns:
            Preferred channel.
        """
        # Could extend this to have per-type preferences
        # For now, use the default
        return prefs.default_channel

    def _is_channel_available(
        self,
        channel: NotificationChannel,
        config: UserChannelConfig,
        prefs: NotificationPreferences,
    ) -> bool:
        """Check if a channel is available and enabled.

        Args:
            channel: Channel to check.
            config: User's channel configuration.
            prefs: User's preferences.

        Returns:
            True if channel can be used.
        """
        if channel == NotificationChannel.EMAIL:
            return bool(config.email) and prefs.email_enabled
        elif channel == NotificationChannel.TELEGRAM:
            return bool(config.telegram_chat_id) and prefs.telegram_enabled
        return False

    def _get_fallback_channel(
        self,
        preferred: NotificationChannel,
        config: UserChannelConfig,
        prefs: NotificationPreferences,
    ) -> NotificationChannel | None:
        """Get fallback channel if preferred is unavailable.

        Args:
            preferred: The preferred channel that's unavailable.
            config: User's channel configuration.
            prefs: User's preferences.

        Returns:
            Fallback channel or None if none available.
        """
        # Try the other channel
        if preferred == NotificationChannel.TELEGRAM:
            if self._is_channel_available(NotificationChannel.EMAIL, config, prefs):
                logger.info(
                    "Falling back to email",
                    preferred="telegram",
                )
                return NotificationChannel.EMAIL
        else:
            if self._is_channel_available(NotificationChannel.TELEGRAM, config, prefs):
                logger.info(
                    "Falling back to Telegram",
                    preferred="email",
                )
                return NotificationChannel.TELEGRAM

        # No channels available
        logger.warning("No notification channels available")
        return None

    def _get_default_channel(
        self,
        config: UserChannelConfig | None,
    ) -> NotificationChannel | None:
        """Get default channel when preferences aren't set.

        Args:
            config: User's channel configuration.

        Returns:
            Default channel or None if none available.
        """
        if not config:
            return None

        # Default preference order: email first
        if config.email:
            return NotificationChannel.EMAIL
        elif config.telegram_chat_id:
            return NotificationChannel.TELEGRAM

        return None


def get_channel_router() -> ChannelRouter:
    """Factory function for dependency injection.

    Returns:
        Configured ChannelRouter instance.
    """
    return ChannelRouter()
