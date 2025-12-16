"""End-of-day summary notification content formatter.

Generates formatted content for EOD summary notifications,
supporting both email and Telegram channels.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class CompletedTask:
    """A completed task in the summary.

    Attributes:
        title: Task title.
        avoidance_weight: Avoidance score 1-5.
    """

    title: str
    avoidance_weight: int = 1


@dataclass
class EODSummaryData:
    """Data for end-of-day summary notification.

    Attributes:
        date: The date of the summary.
        completed: List of completed tasks.
        remaining_count: Number of tasks rolled to tomorrow.
        high_avoidance_wins: Titles of high-avoidance tasks completed.
        ai_summary: Optional AI-generated summary of the day.
    """

    date: date
    completed: list[CompletedTask]
    remaining_count: int = 0
    high_avoidance_wins: list[str] = field(default_factory=list)
    ai_summary: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "EODSummaryData":
        """Create EODSummaryData from a dictionary.

        Args:
            data: Dictionary with completed tasks and summary info.

        Returns:
            EODSummaryData instance.
        """
        completed = [
            CompletedTask(
                title=t.get("title", "Untitled"),
                avoidance_weight=t.get("avoidance_weight", 1),
            )
            for t in data.get("completed", [])
        ]

        summary_date = data.get("date")
        if isinstance(summary_date, str):
            summary_date = date.fromisoformat(summary_date)
        elif summary_date is None:
            summary_date = date.today()

        return cls(
            date=summary_date,
            completed=completed,
            remaining_count=data.get("remaining_count", 0),
            high_avoidance_wins=data.get("high_avoidance_wins", []),
            ai_summary=data.get("ai_summary"),
        )


class EODSummaryContent:
    """Formatter for end-of-day summary notifications.

    Generates formatted content for EOD summary notifications
    in both email (HTML) and Telegram (Markdown) formats.
    """

    def format_email(self, data: EODSummaryData) -> tuple[str, str]:
        """Format EOD summary as email content.

        Args:
            data: EOD summary data.

        Returns:
            Tuple of (subject, html_body).
        """
        completed_count = len(data.completed)
        subject = f"Your day: {completed_count} task{'s' if completed_count != 1 else ''} completed"

        # Build completed list
        completed_html = ""
        for task in data.completed:
            escaped_title = self._escape_html(task.title)
            completed_html += f'<li style="margin: 8px 0;">✓ {escaped_title}</li>'

        if not completed_html:
            completed_html = '<li style="color: #6b7280;">No tasks completed today</li>'

        # Wins section
        wins_html = ""
        if data.high_avoidance_wins:
            wins_items = ""
            for win in data.high_avoidance_wins:
                escaped_win = self._escape_html(win)
                wins_items += f"<li>{escaped_win}</li>"
            wins_html = f"""
            <div style="background: #fef3c7; padding: 16px; border-radius: 8px; margin: 20px 0;">
                <strong style="color: #92400e;">Today's Wins</strong>
                <p style="margin: 8px 0 0 0; color: #78350f;">You pushed through things you'd been avoiding:</p>
                <ul style="margin: 8px 0; padding-left: 20px; color: #78350f;">
                    {wins_items}
                </ul>
            </div>
            """

        # AI summary
        summary_html = ""
        if data.ai_summary:
            escaped_summary = self._escape_html(data.ai_summary)
            summary_html = f"""
            <div style="background: #f3f4f6; padding: 16px; border-radius: 8px; margin: 20px 0; font-style: italic; color: #4b5563;">
                {escaped_summary}
            </div>
            """

        # Remaining note
        remaining_html = ""
        if data.remaining_count > 0:
            task_word = "task" if data.remaining_count == 1 else "tasks"
            remaining_html = f"""
            <p style="color: #6b7280; margin-top: 20px;">
                {data.remaining_count} {task_word} rolled to tomorrow. That's okay - tomorrow is a new day.
            </p>
            """

        body = f"""
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

            <h3>Completed ({completed_count})</h3>
            <ul>
                {completed_html}
            </ul>

            {summary_html}
            {remaining_html}

            <p style="margin-top: 30px; color: #374151;">Rest well. See you tomorrow.</p>
        </div>
        <div class="footer">
            <p>Your Executive Function Prosthetic</p>
        </div>
    </div>
</body>
</html>
        """.strip()

        return subject, body

    def format_telegram(self, data: EODSummaryData) -> str:
        """Format EOD summary as Telegram message.

        Args:
            data: EOD summary data.

        Returns:
            Formatted Telegram message with Markdown.
        """
        completed_count = len(data.completed)
        lines = [f"*Day Complete* - {completed_count} tasks done"]

        # Wins section
        if data.high_avoidance_wins:
            lines.append("")
            lines.append("*Wins*")
            for win in data.high_avoidance_wins:
                escaped_win = self._escape_markdown(win)
                lines.append(f"  {escaped_win}")

        # Completed tasks (limit for readability)
        lines.append("")
        lines.append("*Completed:*")
        for task in data.completed[:5]:
            escaped_title = self._escape_markdown(task.title)
            lines.append(f"✓ {escaped_title}")
        if len(data.completed) > 5:
            lines.append(f"  ...and {len(data.completed) - 5} more")

        # AI summary
        if data.ai_summary:
            lines.append("")
            escaped_summary = self._escape_markdown(data.ai_summary)
            lines.append(f"_{escaped_summary}_")

        # Remaining
        if data.remaining_count > 0:
            lines.append("")
            lines.append(f"{data.remaining_count} tasks rolled to tomorrow.")

        lines.append("")
        lines.append("Rest well.")

        return "\n".join(lines)

    def to_payload_data(self, data: EODSummaryData) -> dict:
        """Convert EODSummaryData to dictionary for NotificationPayload.

        Args:
            data: EOD summary data.

        Returns:
            Dictionary suitable for NotificationPayload.data.
        """
        return {
            "date": data.date.isoformat(),
            "completed": [
                {
                    "title": t.title,
                    "avoidance_weight": t.avoidance_weight,
                }
                for t in data.completed
            ],
            "remaining_count": data.remaining_count,
            "high_avoidance_wins": data.high_avoidance_wins,
            "ai_summary": data.ai_summary,
        }

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters.

        Args:
            text: Text to escape.

        Returns:
            HTML-escaped text.
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _escape_markdown(self, text: str) -> str:
        """Escape Telegram Markdown special characters.

        Args:
            text: Text to escape.

        Returns:
            Markdown-escaped text.
        """
        # Escape characters that have special meaning in Telegram Markdown
        for char in ["_", "*", "`", "["]:
            text = text.replace(char, f"\\{char}")
        return text
