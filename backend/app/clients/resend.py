"""Resend client for transactional emails."""

import re
from typing import Any

import resend
import structlog

from app.config import settings

logger = structlog.get_logger()


class ResendClient:
    """Client wrapper for Resend email API."""

    def __init__(self, api_key: str | None = None, from_email: str | None = None):
        """Initialize Resend client.

        Args:
            api_key: Resend API key. Defaults to settings value.
            from_email: Default sender email. Defaults to settings value.
        """
        self.api_key = api_key or settings.resend_api_key
        if not self.api_key:
            raise ValueError("Resend API key must be configured")

        resend.api_key = self.api_key
        self.from_email = from_email or settings.resend_from_email

    def send_email(
        self,
        to: str | list[str],
        subject: str,
        html: str,
        text: str | None = None
    ) -> str | None:
        """Send an email.

        Args:
            to: Recipient email(s).
            subject: Email subject.
            html: HTML content.
            text: Optional plain text content.

        Returns:
            Message ID if sent, None on failure.
        """
        try:
            result: dict[str, Any] = resend.Emails.send({
                "from": self.from_email,
                "to": to if isinstance(to, list) else [to],
                "subject": subject,
                "html": html,
                "text": text or self._html_to_text(html)
            })

            message_id: str | None = result.get("id")
            logger.info(
                "Email sent",
                to=to,
                subject=subject,
                message_id=message_id
            )
            return message_id

        except Exception as e:
            logger.error(
                "Email send failed",
                to=to,
                subject=subject,
                error=str(e)
            )
            return None

    def _html_to_text(self, html: str) -> str:
        """Simple HTML to text conversion (strip tags).

        Args:
            html: HTML content.

        Returns:
            Plain text version.
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def send_morning_summary(
        self,
        to: str,
        user_name: str,
        tasks: list[dict[str, Any]],
        focus_suggestion: str | None = None
    ) -> str | None:
        """Send morning summary email.

        Args:
            to: Recipient email.
            user_name: User's display name.
            tasks: List of tasks for today.
            focus_suggestion: Optional AI-suggested focus.

        Returns:
            Message ID if sent, None on failure.
        """
        task_list = "\n".join(
            f"<li>{task['title']}</li>" for task in tasks
        ) if tasks else "<li>No tasks scheduled for today</li>"

        focus_html = f"<p><strong>Suggested focus:</strong> {focus_suggestion}</p>" if focus_suggestion else ""

        html = f"""
        <html>
        <body style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Good morning, {user_name}!</h2>
            {focus_html}
            <h3>Today's tasks:</h3>
            <ul>{task_list}</ul>
            <p style="color: #666; font-size: 14px;">
                Remember: Progress over perfection. You've got this.
            </p>
        </body>
        </html>
        """

        return self.send_email(
            to=to,
            subject=f"Your day ahead - {len(tasks)} task{'s' if len(tasks) != 1 else ''}",
            html=html
        )

    def send_eod_summary(
        self,
        to: str,
        user_name: str,
        completed: list[dict[str, Any]],
        carried_over: list[dict[str, Any]],
        streak_days: int = 0
    ) -> str | None:
        """Send end-of-day summary email.

        Args:
            to: Recipient email.
            user_name: User's display name.
            completed: Tasks completed today.
            carried_over: Tasks moving to tomorrow.
            streak_days: Current streak count.

        Returns:
            Message ID if sent, None on failure.
        """
        completed_html = "\n".join(
            f"<li>✓ {task['title']}</li>" for task in completed
        ) if completed else "<li>—</li>"

        carried_html = "\n".join(
            f"<li>→ {task['title']}</li>" for task in carried_over
        ) if carried_over else ""

        streak_html = f"<p>🔥 {streak_days} day streak!</p>" if streak_days > 1 else ""

        html = f"""
        <html>
        <body style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Day complete, {user_name}</h2>
            {streak_html}
            <h3>Completed ({len(completed)}):</h3>
            <ul>{completed_html}</ul>
            {"<h3>Tomorrow:</h3><ul>" + carried_html + "</ul>" if carried_html else ""}
            <p style="color: #666; font-size: 14px;">
                Rest well. Tomorrow is another chance.
            </p>
        </body>
        </html>
        """

        return self.send_email(
            to=to,
            subject=f"Day wrapped - {len(completed)} done",
            html=html
        )


# Factory function for dependency injection
def get_resend_client() -> ResendClient:
    """Get a configured Resend client instance."""
    return ResendClient()
