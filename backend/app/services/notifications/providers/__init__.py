"""Notification providers.

Each provider implements the NotificationProvider interface for a specific channel.
"""

from app.services.notifications.providers.email import (
    EmailProvider,
    get_email_provider,
)
from app.services.notifications.providers.telegram import (
    TelegramNotificationProvider,
    get_telegram_provider,
)

__all__ = [
    "EmailProvider",
    "get_email_provider",
    "TelegramNotificationProvider",
    "get_telegram_provider",
]
