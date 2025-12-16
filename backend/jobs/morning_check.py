"""JOB-001: Morning Check Job

Scheduled job that runs hourly to send morning plan notifications
to users at their local morning hour (8am by default). Fetches
today's planned tasks and sends via the notification gateway.

Usage:
    python -m jobs.morning_check

Cron (Railway):
    0 * * * *  python -m jobs.morning_check
"""

import asyncio
import sys
from datetime import date, datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clients.supabase import get_client
from app.logging_config import configure_logging, get_logger
from app.utils.timezone import is_users_local_hour
from app.services.notifications.base import (
    NotificationPayload,
    NotificationType,
)
from app.services.notifications.gateway import get_notification_gateway
from app.services.notifications.content.morning import (
    MorningPlanContent,
    MorningPlanData,
    PlanTask,
)

# Configure logging for job
configure_logging()
logger = get_logger(__name__)

# Target hour for morning notifications (8am local time)
MORNING_HOUR = 8


async def get_users_at_morning_hour() -> list[dict]:
    """Get users whose local time is currently morning hour.

    Also checks that notifications are enabled for the user.

    Returns:
        List of user profile dicts for users at morning hour.
    """
    supabase = get_client()

    # Fetch all profiles with notifications enabled
    result = supabase.table("profiles").select(
        "id, timezone, notification_enabled"
    ).eq(
        "notification_enabled", True
    ).execute()

    if not result.data:
        return []

    # Filter to users at morning hour
    matching_users = [
        user for user in result.data
        if is_users_local_hour(user.get("timezone", "UTC"), MORNING_HOUR)
    ]

    return matching_users


async def get_user_planned_tasks(user_id: str, plan_date: date) -> list[dict]:
    """Get user's planned tasks for a specific date.

    Args:
        user_id: UUID of user.
        plan_date: Date to fetch tasks for.

    Returns:
        List of action dicts with title, estimated_minutes, avoidance_weight.
    """
    supabase = get_client()

    result = supabase.table("actions").select(
        "id, title, estimated_minutes, avoidance_weight"
    ).eq(
        "user_id", user_id
    ).eq(
        "planned_date", plan_date.isoformat()
    ).in_(
        "status", ["planned", "active"]
    ).order(
        "created_at"
    ).execute()

    return result.data if result.data else []


async def send_morning_notification(user_id: str, tasks: list[dict]) -> bool:
    """Send morning plan notification to user.

    Args:
        user_id: UUID of user.
        tasks: List of planned tasks.

    Returns:
        True if notification sent successfully.
    """
    # Build plan data
    plan_tasks = [
        PlanTask(
            title=task.get("title", "Untitled"),
            estimated_minutes=task.get("estimated_minutes", 0),
            avoidance_weight=task.get("avoidance_weight", 1),
        )
        for task in tasks
    ]

    total_minutes = sum(t.estimated_minutes for t in plan_tasks)

    plan_data = MorningPlanData(
        date=date.today(),
        tasks=plan_tasks,
        total_minutes=total_minutes,
    )

    # Format content
    formatter = MorningPlanContent()
    subject, _html_body = formatter.format_email(plan_data)

    # Create payload
    payload = NotificationPayload(
        user_id=user_id,
        notification_type=NotificationType.MORNING_PLAN,
        subject=subject,
        body=formatter.format_telegram(plan_data),
        data=formatter.to_payload_data(plan_data),
    )

    # Send via gateway
    gateway = get_notification_gateway()
    result = await gateway.send(payload)

    return result.success


async def run_morning_check() -> None:
    """Main job: send morning plan notifications."""
    logger.info(
        "Starting morning check job",
        target_hour=MORNING_HOUR,
        utc_time=datetime.utcnow().isoformat(),
    )

    try:
        # Get users at morning hour
        users = await get_users_at_morning_hour()

        logger.info(
            "Found users at morning hour",
            user_count=len(users),
            target_hour=MORNING_HOUR,
        )

        sent_count = 0
        failed_count = 0
        today = date.today()

        for user in users:
            user_id = user["id"]

            try:
                # Get planned tasks
                tasks = await get_user_planned_tasks(user_id, today)

                # Send notification
                success = await send_morning_notification(user_id, tasks)

                if success:
                    sent_count += 1
                    logger.info(
                        "Sent morning notification",
                        user_id=user_id,
                        task_count=len(tasks),
                    )
                else:
                    failed_count += 1
                    logger.warning(
                        "Failed to send morning notification",
                        user_id=user_id,
                    )

            except Exception as e:
                failed_count += 1
                logger.error(
                    "Error processing user for morning check",
                    user_id=user_id,
                    error=str(e),
                )
                # Continue with other users

        logger.info(
            "Morning check job complete",
            users_processed=len(users),
            notifications_sent=sent_count,
            notifications_failed=failed_count,
        )

    except Exception as e:
        logger.error(
            "Morning check job failed",
            error=str(e),
        )
        raise


def main() -> None:
    """Entry point for running the job."""
    asyncio.run(run_morning_check())


if __name__ == "__main__":
    main()
