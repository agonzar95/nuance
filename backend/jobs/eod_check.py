"""JOB-002: EOD Check Job

Scheduled job that runs hourly to send end-of-day summary notifications
to users at their local evening hour (9pm by default). Fetches completed
tasks, calculates wins, and sends summary via the notification gateway.

Usage:
    python -m jobs.eod_check

Cron (Railway):
    0 * * * *  python -m jobs.eod_check
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
from app.services.notifications.content.eod import (
    EODSummaryContent,
    EODSummaryData,
    CompletedTask,
)

# Configure logging for job
configure_logging()
logger = get_logger(__name__)

# Target hour for EOD notifications (9pm local time)
EOD_HOUR = 21

# Avoidance weight threshold for "high avoidance wins"
HIGH_AVOIDANCE_THRESHOLD = 4


async def get_users_at_eod_hour() -> list[dict]:
    """Get users whose local time is currently EOD hour.

    Also checks that notifications are enabled for the user.

    Returns:
        List of user profile dicts for users at EOD hour.
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

    # Filter to users at EOD hour
    matching_users = [
        user for user in result.data
        if is_users_local_hour(user.get("timezone", "UTC"), EOD_HOUR)
    ]

    return matching_users


async def get_user_completed_tasks(user_id: str, completed_date: date) -> list[dict]:
    """Get user's completed tasks for a specific date.

    Args:
        user_id: UUID of user.
        completed_date: Date to fetch completed tasks for.

    Returns:
        List of completed action dicts.
    """
    supabase = get_client()

    # Get tasks completed today (check updated_at date and status)
    # We look for tasks that are completed and were updated today
    start_of_day = datetime.combine(completed_date, datetime.min.time()).isoformat()
    end_of_day = datetime.combine(completed_date, datetime.max.time()).isoformat()

    result = supabase.table("actions").select(
        "id, title, avoidance_weight, updated_at"
    ).eq(
        "user_id", user_id
    ).eq(
        "status", "completed"
    ).gte(
        "updated_at", start_of_day
    ).lte(
        "updated_at", end_of_day
    ).order(
        "updated_at"
    ).execute()

    return result.data if result.data else []


async def get_user_remaining_tasks(user_id: str, plan_date: date) -> int:
    """Get count of remaining (not completed) tasks for today.

    Args:
        user_id: UUID of user.
        plan_date: Date to check.

    Returns:
        Count of remaining tasks.
    """
    supabase = get_client()

    result = supabase.table("actions").select(
        "id", count="exact"
    ).eq(
        "user_id", user_id
    ).eq(
        "planned_date", plan_date.isoformat()
    ).in_(
        "status", ["planned", "active"]
    ).execute()

    return result.count if result.count else 0


async def send_eod_notification(
    user_id: str,
    completed_tasks: list[dict],
    remaining_count: int,
) -> bool:
    """Send EOD summary notification to user.

    Args:
        user_id: UUID of user.
        completed_tasks: List of completed tasks.
        remaining_count: Number of remaining tasks.

    Returns:
        True if notification sent successfully.
    """
    # Build completed task list
    completed = [
        CompletedTask(
            title=task.get("title", "Untitled"),
            avoidance_weight=task.get("avoidance_weight", 1),
        )
        for task in completed_tasks
    ]

    # Identify high-avoidance wins
    high_avoidance_wins = [
        task.get("title", "Untitled")
        for task in completed_tasks
        if task.get("avoidance_weight", 1) >= HIGH_AVOIDANCE_THRESHOLD
    ]

    summary_data = EODSummaryData(
        date=date.today(),
        completed=completed,
        remaining_count=remaining_count,
        high_avoidance_wins=high_avoidance_wins,
        ai_summary=None,  # Could add AI summary generation later
    )

    # Format content
    formatter = EODSummaryContent()
    subject, _html_body = formatter.format_email(summary_data)

    # Create payload
    payload = NotificationPayload(
        user_id=user_id,
        notification_type=NotificationType.EOD_SUMMARY,
        subject=subject,
        body=formatter.format_telegram(summary_data),
        data=formatter.to_payload_data(summary_data),
    )

    # Send via gateway
    gateway = get_notification_gateway()
    result = await gateway.send(payload)

    return result.success


async def run_eod_check() -> None:
    """Main job: send EOD summary notifications."""
    logger.info(
        "Starting EOD check job",
        target_hour=EOD_HOUR,
        utc_time=datetime.utcnow().isoformat(),
    )

    try:
        # Get users at EOD hour
        users = await get_users_at_eod_hour()

        logger.info(
            "Found users at EOD hour",
            user_count=len(users),
            target_hour=EOD_HOUR,
        )

        sent_count = 0
        failed_count = 0
        today = date.today()

        for user in users:
            user_id = user["id"]

            try:
                # Get completed and remaining tasks
                completed_tasks = await get_user_completed_tasks(user_id, today)
                remaining_count = await get_user_remaining_tasks(user_id, today)

                # Skip if no activity today (nothing completed, nothing planned)
                if not completed_tasks and remaining_count == 0:
                    logger.debug(
                        "Skipping user with no activity",
                        user_id=user_id,
                    )
                    continue

                # Send notification
                success = await send_eod_notification(
                    user_id,
                    completed_tasks,
                    remaining_count,
                )

                if success:
                    sent_count += 1
                    logger.info(
                        "Sent EOD notification",
                        user_id=user_id,
                        completed_count=len(completed_tasks),
                        remaining_count=remaining_count,
                    )
                else:
                    failed_count += 1
                    logger.warning(
                        "Failed to send EOD notification",
                        user_id=user_id,
                    )

            except Exception as e:
                failed_count += 1
                logger.error(
                    "Error processing user for EOD check",
                    user_id=user_id,
                    error=str(e),
                )
                # Continue with other users

        logger.info(
            "EOD check job complete",
            users_processed=len(users),
            notifications_sent=sent_count,
            notifications_failed=failed_count,
        )

    except Exception as e:
        logger.error(
            "EOD check job failed",
            error=str(e),
        )
        raise


def main() -> None:
    """Entry point for running the job."""
    asyncio.run(run_eod_check())


if __name__ == "__main__":
    main()
