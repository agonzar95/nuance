"""JOB-003: Idle Nudge Job

Scheduled job that runs daily to send gentle check-in messages
to users who haven't been active in 3+ days. Helps prevent users
from falling off completely without being pushy or shaming.

Usage:
    python -m jobs.idle_nudge

Cron (Railway):
    0 12 * * *  python -m jobs.idle_nudge
    (Runs daily at noon UTC)
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clients.supabase import get_client
from app.logging_config import configure_logging, get_logger
from app.services.notifications.base import (
    NotificationPayload,
    NotificationType,
)
from app.services.notifications.gateway import get_notification_gateway

# Configure logging for job
configure_logging()
logger = get_logger(__name__)

# Inactivity threshold in days
INACTIVITY_DAYS = 3

# Gentle, non-shaming check-in message
NUDGE_MESSAGE = (
    "Hey! Just checking in. No pressure - "
    "when you're ready, I'm here to help you capture "
    "what's on your mind. One small thing at a time."
)

NUDGE_SUBJECT = "Checking in"


async def get_inactive_users(since: datetime) -> list[dict]:
    """Get users who haven't been active since the given timestamp.

    Uses the get_inactive_users SQL function to find users with:
    - No actions created since
    - No messages sent since
    - No actions updated since
    - Notifications enabled

    Args:
        since: Timestamp to check activity from.

    Returns:
        List of profile dicts for inactive users.
    """
    supabase = get_client()

    try:
        # Call the RPC function
        result = supabase.rpc(
            "get_inactive_users",
            {"since": since.isoformat()}
        ).execute()

        return result.data if result.data else []
    except Exception as e:
        # If the function doesn't exist, fall back to a direct query
        logger.warning(
            "get_inactive_users RPC failed, using fallback query",
            error=str(e),
        )
        return await get_inactive_users_fallback(since)


async def get_inactive_users_fallback(since: datetime) -> list[dict]:
    """Fallback query if RPC function doesn't exist.

    Performs direct queries to find inactive users.

    Args:
        since: Timestamp to check activity from.

    Returns:
        List of profile dicts for inactive users.
    """
    supabase = get_client()

    # Get all profiles with notifications enabled
    profiles_result = supabase.table("profiles").select(
        "id, timezone, notification_enabled, telegram_chat_id"
    ).eq(
        "notification_enabled", True
    ).execute()

    if not profiles_result.data:
        return []

    inactive_users = []
    since_iso = since.isoformat()

    for profile in profiles_result.data:
        user_id = profile["id"]

        # Check for recent actions
        actions_result = supabase.table("actions").select(
            "id", count="exact"
        ).eq(
            "user_id", user_id
        ).gt(
            "updated_at", since_iso
        ).limit(1).execute()

        if actions_result.count and actions_result.count > 0:
            continue  # User has recent activity

        # Check for recent messages
        # First get user's conversations
        convos_result = supabase.table("conversations").select(
            "id"
        ).eq(
            "user_id", user_id
        ).execute()

        if convos_result.data:
            convo_ids = [c["id"] for c in convos_result.data]
            messages_result = supabase.table("messages").select(
                "id", count="exact"
            ).in_(
                "conversation_id", convo_ids
            ).eq(
                "role", "user"
            ).gt(
                "created_at", since_iso
            ).limit(1).execute()

            if messages_result.count and messages_result.count > 0:
                continue  # User has recent activity

        # User is inactive
        inactive_users.append(profile)

    return inactive_users


async def send_nudge_notification(user_id: str) -> bool:
    """Send gentle check-in notification to user.

    Args:
        user_id: UUID of user.

    Returns:
        True if notification sent successfully.
    """
    payload = NotificationPayload(
        user_id=user_id,
        notification_type=NotificationType.INACTIVITY_CHECK,
        subject=NUDGE_SUBJECT,
        body=NUDGE_MESSAGE,
        data={"type": "idle_nudge"},
    )

    gateway = get_notification_gateway()
    result = await gateway.send(payload)

    return result.success


async def run_idle_nudge() -> None:
    """Main job: send check-in messages to inactive users."""
    logger.info(
        "Starting idle nudge job",
        inactivity_days=INACTIVITY_DAYS,
        utc_time=datetime.now(timezone.utc).isoformat(),
    )

    try:
        # Calculate the threshold timestamp
        since = datetime.now(timezone.utc) - timedelta(days=INACTIVITY_DAYS)

        # Get inactive users
        users = await get_inactive_users(since)

        logger.info(
            "Found inactive users",
            user_count=len(users),
            inactivity_threshold=since.isoformat(),
        )

        sent_count = 0
        failed_count = 0

        for user in users:
            user_id = user["id"]

            try:
                success = await send_nudge_notification(user_id)

                if success:
                    sent_count += 1
                    logger.info(
                        "Sent idle nudge",
                        user_id=user_id,
                    )
                else:
                    failed_count += 1
                    logger.warning(
                        "Failed to send idle nudge",
                        user_id=user_id,
                    )

            except Exception as e:
                failed_count += 1
                logger.error(
                    "Error sending idle nudge",
                    user_id=user_id,
                    error=str(e),
                )
                # Continue with other users

        logger.info(
            "Idle nudge job complete",
            users_processed=len(users),
            notifications_sent=sent_count,
            notifications_failed=failed_count,
        )

    except Exception as e:
        logger.error(
            "Idle nudge job failed",
            error=str(e),
        )
        raise


def main() -> None:
    """Entry point for running the job."""
    asyncio.run(run_idle_nudge())


if __name__ == "__main__":
    main()
