"""Email notification provider using Resend.

Implements NotificationProvider for sending email notifications.
"""

import asyncio
from datetime import datetime, UTC

import structlog

from app.clients.resend import ResendClient, get_resend_client
from app.clients.supabase import get_supabase_client
from app.services.notifications.base import (
    NotificationChannel,
    NotificationPayload,
    NotificationType,
    DeliveryResult,
    NotificationProvider,
)

logger = structlog.get_logger()

# Retry configuration
MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2  # 2^attempt seconds: 2, 4, 8


class EmailProvider(NotificationProvider):
    """Email notification provider using Resend API.

    Features:
    - Wraps ResendClient for email delivery
    - Exponential backoff retry (3 retries)
    - HTML email formatting
    - Default subjects by notification type
    """

    def __init__(
        self,
        resend_client: ResendClient | None = None,
    ):
        """Initialize email provider.

        Args:
            resend_client: Resend client instance. Defaults to factory.
        """
        self._resend = resend_client or get_resend_client()
        self._supabase = get_supabase_client()

    @property
    def channel(self) -> NotificationChannel:
        """The channel this provider delivers to."""
        return NotificationChannel.EMAIL

    async def send(
        self,
        user_id: str,
        payload: NotificationPayload,
    ) -> DeliveryResult:
        """Send an email notification to a user.

        Args:
            user_id: User to notify.
            payload: Notification content and metadata.

        Returns:
            DeliveryResult indicating success or failure.
        """
        # Get user email
        email = await self._get_user_email(user_id)
        if not email:
            return DeliveryResult(
                success=False,
                channel=NotificationChannel.EMAIL,
                error="User email not found",
            )

        # Prepare email content
        subject = payload.subject or self._default_subject(payload.notification_type)
        html_body = self._format_html(payload)

        # Send with retry
        return await self._send_with_retry(email, subject, html_body)

    async def is_configured_for_user(self, user_id: str) -> bool:
        """Check if email is configured for user.

        Args:
            user_id: User to check.

        Returns:
            True if user has an email address.
        """
        email = await self._get_user_email(user_id)
        return email is not None

    async def _get_user_email(self, user_id: str) -> str | None:
        """Get user's email from Supabase auth.

        Args:
            user_id: User ID.

        Returns:
            Email address or None if not found.
        """
        try:
            # Query auth.users via admin API
            response = self._supabase.auth.admin.get_user_by_id(user_id)
            if response and response.user:
                return response.user.email
            return None
        except Exception as e:
            logger.error("Failed to get user email", user_id=user_id, error=str(e))
            return None

    async def _send_with_retry(
        self,
        to: str,
        subject: str,
        html: str,
    ) -> DeliveryResult:
        """Send email with exponential backoff retry.

        Args:
            to: Recipient email.
            subject: Email subject.
            html: HTML content.

        Returns:
            DeliveryResult with success status and retry count.
        """
        last_error: str | None = None
        retries = 0

        for attempt in range(MAX_RETRIES + 1):  # 0, 1, 2, 3 (initial + 3 retries)
            try:
                # Resend SDK is synchronous, run in thread pool
                message_id = await asyncio.to_thread(
                    self._resend.send_email,
                    to,
                    subject,
                    html,
                )

                if message_id:
                    return DeliveryResult(
                        success=True,
                        channel=NotificationChannel.EMAIL,
                        provider_id=message_id,
                        retries=retries,
                    )
                else:
                    last_error = "Send failed without exception"
                    retries = attempt

            except Exception as e:
                last_error = str(e)
                retries = attempt
                logger.warning(
                    "Email send attempt failed",
                    attempt=attempt + 1,
                    max_attempts=MAX_RETRIES + 1,
                    error=last_error,
                )

            # Exponential backoff before retry (skip on last attempt)
            if attempt < MAX_RETRIES:
                backoff = BASE_BACKOFF_SECONDS ** (attempt + 1)
                await asyncio.sleep(backoff)

        # All retries exhausted
        logger.error(
            "Email send failed after all retries",
            to=to,
            subject=subject,
            retries=retries,
            error=last_error,
        )

        return DeliveryResult(
            success=False,
            channel=NotificationChannel.EMAIL,
            error=last_error,
            retries=retries,
        )

    def _default_subject(self, notification_type: NotificationType) -> str:
        """Get default subject for notification type.

        Args:
            notification_type: Type of notification.

        Returns:
            Default subject line.
        """
        subjects = {
            NotificationType.MORNING_PLAN: "Your plan for today",
            NotificationType.EOD_SUMMARY: "Your day in review",
            NotificationType.INACTIVITY_CHECK: "Checking in",
            NotificationType.TASK_REMINDER: "Task reminder",
            NotificationType.STREAK_UPDATE: "Keep your streak going!",
        }
        return subjects.get(notification_type, "Notification from Nuance")

    def _format_html(self, payload: NotificationPayload) -> str:
        """Format notification as HTML email.

        Args:
            payload: Notification content.

        Returns:
            HTML email body.
        """
        # Use type-specific formatting if available
        if payload.notification_type == NotificationType.MORNING_PLAN:
            return self._format_morning_plan(payload)
        elif payload.notification_type == NotificationType.EOD_SUMMARY:
            return self._format_eod_summary(payload)

        # Generic template
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            margin: 0;
            padding: 0;
            background-color: #f3f4f6;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 32px 20px;
        }}
        .content {{
            background: #ffffff;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            font-size: 14px;
            color: #6b7280;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            {payload.body}
        </div>
        <div class="footer">
            <p>Your Executive Function Prosthetic</p>
        </div>
    </div>
</body>
</html>
        """.strip()

    def _format_morning_plan(self, payload: NotificationPayload) -> str:
        """Format morning plan email.

        Args:
            payload: Notification with plan data.

        Returns:
            HTML email for morning plan.
        """
        data = payload.data or {}
        tasks = data.get("tasks", [])
        total_minutes = data.get("total_minutes", 0)

        # Format time estimate
        hours = total_minutes // 60
        mins = total_minutes % 60
        time_str = f"{hours}h {mins}m" if hours else f"{mins}m"

        # Build task list
        task_rows = ""
        for task in tasks:
            title = task.get("title", "Untitled")
            est = task.get("estimated_minutes", 0)
            avoidance = task.get("avoidance_weight", 1)
            dots = "●" * avoidance + "○" * (5 - avoidance)
            task_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">
                    <strong>{title}</strong><br>
                    <small style="color: #6b7280;">~{est} min</small>
                </td>
                <td style="padding: 12px; text-align: right; font-size: 10px; color: #9ca3af; border-bottom: 1px solid #f3f4f6;">
                    {dots}
                </td>
            </tr>
            """

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            margin: 0;
            padding: 0;
            background-color: #f3f4f6;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 32px 20px;
        }}
        .content {{
            background: #ffffff;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            margin: 0 0 8px 0;
            font-size: 24px;
            color: #111827;
        }}
        .subtitle {{
            color: #6b7280;
            margin-bottom: 24px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .time-total {{
            background: #f9fafb;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            margin-top: 24px;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            font-size: 14px;
            color: #6b7280;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <h1>Good morning!</h1>
            <p class="subtitle">Here's your plan for today:</p>

            <table>
                {task_rows if task_rows else '<tr><td style="padding: 12px; color: #6b7280;">No tasks planned yet. Open the app to add some!</td></tr>'}
            </table>

            <div class="time-total">
                <strong>Total planned time:</strong> {time_str}
            </div>

            {payload.body if payload.body else ""}
        </div>
        <div class="footer">
            <p>Your Executive Function Prosthetic</p>
        </div>
    </div>
</body>
</html>
        """.strip()

    def _format_eod_summary(self, payload: NotificationPayload) -> str:
        """Format end-of-day summary email.

        Args:
            payload: Notification with summary data.

        Returns:
            HTML email for EOD summary.
        """
        data = payload.data or {}
        completed = data.get("completed", [])
        remaining_count = data.get("remaining_count", 0)
        high_avoidance_wins = data.get("high_avoidance_wins", [])
        ai_summary = data.get("ai_summary")

        # Build completed list
        completed_html = ""
        for task in completed:
            title = task.get("title", "Untitled")
            completed_html += f'<li style="margin: 8px 0;">✓ {title}</li>'

        # Wins section
        wins_html = ""
        if high_avoidance_wins:
            wins_items = "".join(f"<li>{win}</li>" for win in high_avoidance_wins)
            wins_html = f"""
            <div style="background: #fef3c7; padding: 16px; border-radius: 8px; margin: 20px 0;">
                <strong style="color: #92400e;">⭐ Today's Wins</strong>
                <p style="margin: 8px 0 0 0; color: #78350f;">You pushed through things you'd been avoiding:</p>
                <ul style="margin: 8px 0; padding-left: 20px; color: #78350f;">
                    {wins_items}
                </ul>
            </div>
            """

        # AI summary
        summary_html = ""
        if ai_summary:
            summary_html = f"""
            <div style="background: #f3f4f6; padding: 16px; border-radius: 8px; margin: 20px 0; font-style: italic; color: #4b5563;">
                {ai_summary}
            </div>
            """

        # Remaining note
        remaining_html = ""
        if remaining_count > 0:
            remaining_html = f"""
            <p style="color: #6b7280; margin-top: 20px;">
                {remaining_count} task{'s' if remaining_count != 1 else ''} rolled to tomorrow. That's okay - tomorrow is a new day.
            </p>
            """

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            margin: 0;
            padding: 0;
            background-color: #f3f4f6;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 32px 20px;
        }}
        .content {{
            background: #ffffff;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            margin: 0 0 24px 0;
            font-size: 24px;
            color: #111827;
        }}
        h3 {{
            margin: 24px 0 12px 0;
            color: #374151;
        }}
        ul {{
            padding-left: 20px;
            margin: 0;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            font-size: 14px;
            color: #6b7280;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <h1>Day Complete</h1>

            {wins_html}

            <h3>Completed ({len(completed)})</h3>
            <ul>
                {completed_html if completed_html else '<li style="color: #6b7280;">No tasks completed today</li>'}
            </ul>

            {summary_html}
            {remaining_html}

            <p style="margin-top: 30px; color: #374151;">Rest well. See you tomorrow.</p>

            {payload.body if payload.body else ""}
        </div>
        <div class="footer">
            <p>Your Executive Function Prosthetic</p>
        </div>
    </div>
</body>
</html>
        """.strip()


def get_email_provider() -> EmailProvider:
    """Factory function for dependency injection.

    Returns:
        Configured EmailProvider instance.
    """
    return EmailProvider()
