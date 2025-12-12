"""Telegram notification provider.

Implements NotificationProvider for sending Telegram notifications.
"""

import structlog

from app.clients.telegram import TelegramClient, get_telegram_client
from app.clients.supabase import get_supabase_client
from app.services.notifications.base import (
    NotificationChannel,
    NotificationPayload,
    NotificationType,
    DeliveryResult,
    NotificationProvider,
)

logger = structlog.get_logger()


class TelegramNotificationProvider(NotificationProvider):
    """Telegram notification provider using Bot API.

    Features:
    - Wraps TelegramClient for message delivery
    - Markdown message formatting
    - Type-specific message templates
    """

    def __init__(
        self,
        telegram_client: TelegramClient | None = None,
    ):
        """Initialize Telegram provider.

        Args:
            telegram_client: Telegram client instance. Defaults to factory.
        """
        self._telegram = telegram_client or get_telegram_client()
        self._supabase = get_supabase_client()

    @property
    def channel(self) -> NotificationChannel:
        """The channel this provider delivers to."""
        return NotificationChannel.TELEGRAM

    async def send(
        self,
        user_id: str,
        payload: NotificationPayload,
    ) -> DeliveryResult:
        """Send a Telegram notification to a user.

        Args:
            user_id: User to notify.
            payload: Notification content and metadata.

        Returns:
            DeliveryResult indicating success or failure.
        """
        # Get user's Telegram chat ID
        chat_id = await self._get_chat_id(user_id)
        if not chat_id:
            return DeliveryResult(
                success=False,
                channel=NotificationChannel.TELEGRAM,
                error="User Telegram not connected",
            )

        # Format message
        text = self._format_message(payload)

        # Send message
        return await self.send_message(chat_id, text)

    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "Markdown",
    ) -> DeliveryResult:
        """Send a message to a specific chat.

        Args:
            chat_id: Telegram chat ID.
            text: Message text.
            parse_mode: Message formatting (Markdown, HTML).

        Returns:
            DeliveryResult indicating success or failure.
        """
        try:
            success = await self._telegram.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
            )

            if success:
                return DeliveryResult(
                    success=True,
                    channel=NotificationChannel.TELEGRAM,
                    # Note: TelegramClient.send_message returns bool, not message_id
                    # We could enhance it to return message_id if needed
                    provider_id=None,
                )
            else:
                return DeliveryResult(
                    success=False,
                    channel=NotificationChannel.TELEGRAM,
                    error="Message send failed",
                )

        except Exception as e:
            logger.error(
                "Telegram send error",
                chat_id=chat_id,
                error=str(e),
            )
            return DeliveryResult(
                success=False,
                channel=NotificationChannel.TELEGRAM,
                error=str(e),
            )

    async def is_configured_for_user(self, user_id: str) -> bool:
        """Check if Telegram is configured for user.

        Args:
            user_id: User to check.

        Returns:
            True if user has a connected Telegram account.
        """
        chat_id = await self._get_chat_id(user_id)
        return chat_id is not None

    async def _get_chat_id(self, user_id: str) -> str | None:
        """Get user's Telegram chat ID from profile.

        Args:
            user_id: User ID.

        Returns:
            Telegram chat ID or None if not connected.
        """
        try:
            response = (
                self._supabase.table("profiles")
                .select("telegram_chat_id")
                .eq("id", user_id)
                .single()
                .execute()
            )

            if response.data and isinstance(response.data, dict):
                chat_id = response.data.get("telegram_chat_id")
                return str(chat_id) if chat_id else None
            return None

        except Exception as e:
            logger.error("Failed to get chat ID", user_id=user_id, error=str(e))
            return None

    def _format_message(self, payload: NotificationPayload) -> str:
        """Format notification as Telegram message.

        Args:
            payload: Notification content.

        Returns:
            Formatted message text with Markdown.
        """
        if payload.notification_type == NotificationType.MORNING_PLAN:
            return self._format_morning_plan(payload)
        elif payload.notification_type == NotificationType.EOD_SUMMARY:
            return self._format_eod_summary(payload)
        elif payload.notification_type == NotificationType.INACTIVITY_CHECK:
            return self._format_inactivity_check(payload)

        # Generic format
        if payload.subject:
            return f"*{payload.subject}*\n\n{payload.body}"
        return payload.body

    def _format_morning_plan(self, payload: NotificationPayload) -> str:
        """Format morning plan as Telegram message.

        Args:
            payload: Notification with plan data.

        Returns:
            Formatted message.
        """
        data = payload.data or {}
        tasks = data.get("tasks", [])
        total_minutes = data.get("total_minutes", 0)

        # Format time
        hours = total_minutes // 60
        mins = total_minutes % 60
        time_str = f"{hours}h {mins}m" if hours else f"{mins}m"

        # Build task list
        task_lines = []
        for task in tasks:
            title = task.get("title", "Untitled")
            est = task.get("estimated_minutes", 0)
            avoidance = task.get("avoidance_weight", 1)
            dots = "●" * avoidance if avoidance > 1 else ""
            task_lines.append(f"• {title} (~{est}min) {dots}")

        tasks_str = "\n".join(task_lines) if task_lines else "No tasks planned"

        return f"""*Good morning!*

Here's your plan for today:

{tasks_str}

Total: {time_str}

You've got this."""

    def _format_eod_summary(self, payload: NotificationPayload) -> str:
        """Format EOD summary as Telegram message.

        Args:
            payload: Notification with summary data.

        Returns:
            Formatted message.
        """
        data = payload.data or {}
        completed = data.get("completed", [])
        remaining_count = data.get("remaining_count", 0)
        high_avoidance_wins = data.get("high_avoidance_wins", [])
        ai_summary = data.get("ai_summary")

        lines = [f"*Day Complete* - {len(completed)} tasks done"]

        # Wins section
        if high_avoidance_wins:
            lines.append("")
            lines.append("⭐ *Wins*")
            for win in high_avoidance_wins:
                lines.append(f"  {win}")

        # Completed tasks (limit for readability)
        lines.append("")
        lines.append("*Completed:*")
        for task in completed[:5]:
            title = task.get("title", "Untitled")
            lines.append(f"✓ {title}")
        if len(completed) > 5:
            lines.append(f"  ...and {len(completed) - 5} more")

        # AI summary
        if ai_summary:
            lines.append("")
            lines.append(f"_{ai_summary}_")

        # Remaining
        if remaining_count > 0:
            lines.append("")
            lines.append(f"{remaining_count} tasks rolled to tomorrow.")

        lines.append("")
        lines.append("Rest well.")

        return "\n".join(lines)

    def _format_inactivity_check(self, payload: NotificationPayload) -> str:
        """Format inactivity check message.

        Args:
            payload: Notification data.

        Returns:
            Formatted message.
        """
        data = payload.data or {}
        days_inactive = data.get("days_inactive", 1)
        pending_count = data.get("pending_count", 0)

        if days_inactive > 3:
            greeting = "Hey, it's been a while!"
        else:
            greeting = "Checking in"

        message = f"*{greeting}*\n\n"

        if pending_count > 0:
            message += f"You have {pending_count} task{'s' if pending_count != 1 else ''} waiting.\n\n"
        else:
            message += "No pressure - just wanted to say hi.\n\n"

        message += "What's on your mind?"

        return message


def get_telegram_provider() -> TelegramNotificationProvider:
    """Factory function for dependency injection.

    Returns:
        Configured TelegramNotificationProvider instance.
    """
    return TelegramNotificationProvider()
