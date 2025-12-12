"""Base types and interfaces for notification system.

Defines the core abstractions used by all notification components.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any


class NotificationChannel(str, Enum):
    """Available notification delivery channels."""

    EMAIL = "email"
    TELEGRAM = "telegram"


class NotificationType(str, Enum):
    """Types of notifications the system can send."""

    MORNING_PLAN = "morning_plan"
    EOD_SUMMARY = "eod_summary"
    INACTIVITY_CHECK = "inactivity_check"
    TASK_REMINDER = "task_reminder"
    STREAK_UPDATE = "streak_update"
    CUSTOM = "custom"


@dataclass
class NotificationPayload:
    """Payload for a notification to be sent.

    Attributes:
        user_id: The user to notify.
        notification_type: Type of notification being sent.
        subject: Optional subject line (used for email).
        body: Main content of the notification.
        data: Additional data for template rendering.
        priority: Notification priority (higher = more important).
    """

    user_id: str
    notification_type: NotificationType
    subject: str | None = None
    body: str = ""
    data: dict[str, Any] | None = None
    priority: int = 0


@dataclass
class DeliveryResult:
    """Result of attempting to deliver a notification.

    Attributes:
        success: Whether delivery succeeded.
        channel: Channel used for delivery.
        provider_id: Provider's message/delivery ID.
        error: Error message if delivery failed.
        timestamp: When delivery was attempted.
        retries: Number of retry attempts made.
    """

    success: bool
    channel: NotificationChannel
    provider_id: str | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    retries: int = 0


class NotificationProvider(ABC):
    """Abstract base class for notification providers.

    Each channel (email, Telegram, etc.) implements this interface
    to provide a consistent way to send notifications.
    """

    @property
    @abstractmethod
    def channel(self) -> NotificationChannel:
        """The channel this provider delivers to."""
        pass

    @abstractmethod
    async def send(
        self,
        user_id: str,
        payload: NotificationPayload,
    ) -> DeliveryResult:
        """Send a notification to a user.

        Args:
            user_id: User to notify.
            payload: Notification content and metadata.

        Returns:
            DeliveryResult indicating success or failure.
        """
        pass

    @abstractmethod
    async def is_configured_for_user(self, user_id: str) -> bool:
        """Check if this channel is configured for a user.

        Args:
            user_id: User to check.

        Returns:
            True if user can receive notifications on this channel.
        """
        pass
