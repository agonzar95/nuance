"""Notification services.

This module provides the notification infrastructure for Nuance:
- Gateway abstraction for unified notification sending
- Email provider (Resend)
- Telegram provider
- Channel routing based on user preferences
"""

from app.services.notifications.base import (
    NotificationChannel,
    NotificationType,
    NotificationPayload,
    DeliveryResult,
    NotificationProvider,
)
from app.services.notifications.router import (
    ChannelRouter,
    NotificationPreferences,
    UserChannelConfig,
    get_channel_router,
)
from app.services.notifications.gateway import (
    NotificationGateway,
    get_notification_gateway,
)

__all__ = [
    # Base types
    "NotificationChannel",
    "NotificationType",
    "NotificationPayload",
    "DeliveryResult",
    "NotificationProvider",
    # Router
    "ChannelRouter",
    "NotificationPreferences",
    "UserChannelConfig",
    "get_channel_router",
    # Gateway
    "NotificationGateway",
    "get_notification_gateway",
]
