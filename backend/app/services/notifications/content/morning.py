"""Morning plan notification content formatter.

Generates formatted content for morning plan notifications,
supporting both email and Telegram channels.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class PlanTask:
    """A task in the morning plan.

    Attributes:
        title: Task title.
        estimated_minutes: Estimated time in minutes.
        avoidance_weight: Avoidance score 1-5.
    """

    title: str
    estimated_minutes: int
    avoidance_weight: int = 1


@dataclass
class MorningPlanData:
    """Data for morning plan notification.

    Attributes:
        date: The date of the plan.
        tasks: List of planned tasks.
        total_minutes: Total planned time.
    """

    date: date
    tasks: list[PlanTask]
    total_minutes: int

    @classmethod
    def from_dict(cls, data: dict) -> "MorningPlanData":
        """Create MorningPlanData from a dictionary.

        Args:
            data: Dictionary with tasks, total_minutes, and optional date.

        Returns:
            MorningPlanData instance.
        """
        tasks = [
            PlanTask(
                title=t.get("title", "Untitled"),
                estimated_minutes=t.get("estimated_minutes", 0),
                avoidance_weight=t.get("avoidance_weight", 1),
            )
            for t in data.get("tasks", [])
        ]
        plan_date = data.get("date")
        if isinstance(plan_date, str):
            plan_date = date.fromisoformat(plan_date)
        elif plan_date is None:
            plan_date = date.today()

        return cls(
            date=plan_date,
            tasks=tasks,
            total_minutes=data.get("total_minutes", 0),
        )


class MorningPlanContent:
    """Formatter for morning plan notifications.

    Generates formatted content for morning plan notifications
    in both email (HTML) and Telegram (Markdown) formats.
    """

    def format_email(self, data: MorningPlanData) -> tuple[str, str]:
        """Format morning plan as email content.

        Args:
            data: Morning plan data.

        Returns:
            Tuple of (subject, html_body).
        """
        subject = f"Your plan for {data.date.strftime('%A, %B %d')}"

        # Format time estimate
        hours = data.total_minutes // 60
        mins = data.total_minutes % 60
        time_str = f"{hours}h {mins}m" if hours else f"{mins}m"

        # Build task table rows
        task_rows = ""
        for task in data.tasks:
            dots = "●" * task.avoidance_weight + "○" * (5 - task.avoidance_weight)
            task_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">
                    <strong>{self._escape_html(task.title)}</strong><br>
                    <small style="color: #6b7280;">~{task.estimated_minutes} min</small>
                </td>
                <td style="padding: 12px; text-align: right; font-size: 10px; color: #9ca3af; border-bottom: 1px solid #f3f4f6;">
                    {dots}
                </td>
            </tr>
            """

        no_tasks_row = '<tr><td style="padding: 12px; color: #6b7280;">No tasks planned yet. Open the app to add some!</td></tr>'

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
        .cta-button {{
            display: inline-block;
            background: #4F46E5;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
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
                {task_rows if task_rows else no_tasks_row}
            </table>

            <div class="time-total">
                <strong>Total planned time:</strong> {time_str}
            </div>

            <p style="text-align: center;">
                <a href="https://app.nuance.dev/plan" class="cta-button">
                    Open Today View
                </a>
            </p>
        </div>
        <div class="footer">
            <p>Your Executive Function Prosthetic</p>
        </div>
    </div>
</body>
</html>
        """.strip()

        return subject, body

    def format_telegram(self, data: MorningPlanData) -> str:
        """Format morning plan as Telegram message.

        Args:
            data: Morning plan data.

        Returns:
            Formatted Telegram message with Markdown.
        """
        day_name = data.date.strftime("%A")

        # Format time estimate
        hours = data.total_minutes // 60
        mins = data.total_minutes % 60
        time_str = f"{hours}h {mins}m" if hours else f"{mins}m"

        # Build task list
        task_lines = []
        for task in data.tasks:
            dots = "●" * task.avoidance_weight if task.avoidance_weight > 1 else ""
            escaped_title = self._escape_markdown(task.title)
            task_lines.append(f"• {escaped_title} (~{task.estimated_minutes}min) {dots}")

        tasks_str = "\n".join(task_lines) if task_lines else "No tasks planned"

        return f"""*Good morning!* Happy {day_name}.

Here's your plan for today:

{tasks_str}

Total: {time_str}

You've got this."""

    def to_payload_data(self, data: MorningPlanData) -> dict:
        """Convert MorningPlanData to dictionary for NotificationPayload.

        Args:
            data: Morning plan data.

        Returns:
            Dictionary suitable for NotificationPayload.data.
        """
        return {
            "date": data.date.isoformat(),
            "tasks": [
                {
                    "title": t.title,
                    "estimated_minutes": t.estimated_minutes,
                    "avoidance_weight": t.avoidance_weight,
                }
                for t in data.tasks
            ],
            "total_minutes": data.total_minutes,
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
