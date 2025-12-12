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

__all__ = [
    "NotificationChannel",
    "NotificationType",
    "NotificationPayload",
    "DeliveryResult",
    "NotificationProvider",
]
