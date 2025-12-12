"""SUB-009: Job: State Transitions

Scheduled job that runs hourly to transition action states at the start
of each user's day (4am local time). This ensures that unfinished
"planned" or "active" actions from the previous day are rolled over,
giving users a clean slate each morning.

Usage:
    python -m jobs.state_transitions

Cron (Railway):
    0 * * * *  python -m jobs.state_transitions
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clients.supabase import get_client
from app.logging_config import configure_logging, get_logger
from app.utils.timezone import is_users_local_hour

# Configure logging for job
configure_logging()
logger = get_logger(__name__)

# Target hour for state transitions (4am local time)
TRANSITION_HOUR = 4


async def get_users_at_local_hour(target_hour: int) -> list[dict[str, str]]:
    """Get users whose local time is currently at target_hour.

    Args:
        target_hour: Hour (0-23) to match

    Returns:
        List of user profile dicts for users at target hour
    """
    supabase = get_client()

    # Fetch all profiles with their timezones
    result = supabase.table("profiles").select("id, timezone").execute()

    if not result.data:
        return []

    # Filter to users at target hour
    matching_users = [
        user for user in result.data
        if is_users_local_hour(user.get("timezone", "UTC"), target_hour)
    ]

    return matching_users


async def roll_user_actions(user_id: str) -> int:
    """Roll over user's unfinished actions from previous day.

    Transitions actions with status 'planned' or 'active' to 'rolled'
    and clears their planned_date.

    Args:
        user_id: UUID of user

    Returns:
        Number of actions rolled
    """
    supabase = get_client()

    # Update planned/active actions to rolled
    result = supabase.table("actions").update({
        "status": "rolled",
        "planned_date": None,
        "updated_at": datetime.utcnow().isoformat(),
    }).eq(
        "user_id", user_id
    ).in_(
        "status", ["planned", "active"]
    ).execute()

    return len(result.data) if result.data else 0


async def run_state_transitions() -> None:
    """Main job: transition states for all users at 4am local time."""
    logger.info(
        "Starting state transitions job",
        target_hour=TRANSITION_HOUR,
        utc_time=datetime.utcnow().isoformat(),
    )

    try:
        # Get users whose local time is 4am
        users = await get_users_at_local_hour(TRANSITION_HOUR)

        logger.info(
            "Found users at target hour",
            user_count=len(users),
            target_hour=TRANSITION_HOUR,
        )

        total_rolled = 0

        for user in users:
            user_id = user["id"]

            try:
                rolled_count = await roll_user_actions(user_id)
                total_rolled += rolled_count

                if rolled_count > 0:
                    logger.info(
                        "Rolled user actions",
                        user_id=user_id,
                        rolled_count=rolled_count,
                    )

            except Exception as e:
                logger.error(
                    "Failed to roll actions for user",
                    user_id=user_id,
                    error=str(e),
                )
                # Continue with other users

        logger.info(
            "State transitions job complete",
            users_processed=len(users),
            total_actions_rolled=total_rolled,
        )

    except Exception as e:
        logger.error(
            "State transitions job failed",
            error=str(e),
        )
        raise


def main() -> None:
    """Entry point for running the job."""
    asyncio.run(run_state_transitions())


if __name__ == "__main__":
    main()
