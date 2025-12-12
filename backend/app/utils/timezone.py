"""SUB-008: Timezone Handling utilities.

Provides timezone-aware date/time operations for:
- Determining user's local time from stored timezone
- Checking if it's a specific hour in user's timezone (for jobs)
- Converting between UTC and user's local time
"""

from datetime import datetime, date, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from app.logging_config import get_logger

logger = get_logger(__name__)


def get_user_local_time(user_timezone: str) -> datetime:
    """Get the current time in user's timezone.

    Args:
        user_timezone: IANA timezone string (e.g., 'America/New_York')

    Returns:
        Current datetime in user's timezone
    """
    try:
        tz = ZoneInfo(user_timezone)
        return datetime.now(tz)
    except KeyError:
        logger.warning(
            "Invalid timezone, falling back to UTC",
            timezone=user_timezone
        )
        return datetime.now(ZoneInfo("UTC"))


def get_user_local_hour(user_timezone: str) -> int:
    """Get the current hour (0-23) in user's timezone.

    Args:
        user_timezone: IANA timezone string

    Returns:
        Current hour (0-23) in user's timezone
    """
    return get_user_local_time(user_timezone).hour


def get_user_local_date(user_timezone: str) -> date:
    """Get the current date in user's timezone.

    Args:
        user_timezone: IANA timezone string

    Returns:
        Current date in user's timezone
    """
    return get_user_local_time(user_timezone).date()


def is_users_local_hour(user_timezone: str, target_hour: int) -> bool:
    """Check if it's currently a specific hour in user's timezone.

    Used by scheduled jobs to determine if a notification should be sent.

    Args:
        user_timezone: IANA timezone string
        target_hour: Hour to check (0-23)

    Returns:
        True if current hour in user's timezone matches target_hour
    """
    return get_user_local_hour(user_timezone) == target_hour


def utc_to_user_local(
    utc_dt: datetime,
    user_timezone: str
) -> datetime:
    """Convert a UTC datetime to user's local timezone.

    Args:
        utc_dt: Datetime in UTC (should have UTC tzinfo)
        user_timezone: IANA timezone string

    Returns:
        Datetime converted to user's timezone
    """
    try:
        tz = ZoneInfo(user_timezone)
        # Ensure UTC timezone if not set
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))
        return utc_dt.astimezone(tz)
    except KeyError:
        logger.warning(
            "Invalid timezone, returning UTC",
            timezone=user_timezone
        )
        return utc_dt


def user_local_to_utc(
    local_dt: datetime,
    user_timezone: str
) -> datetime:
    """Convert a user's local datetime to UTC.

    Args:
        local_dt: Datetime in user's local timezone
        user_timezone: IANA timezone string

    Returns:
        Datetime converted to UTC
    """
    try:
        tz = ZoneInfo(user_timezone)
        # Localize the datetime if not already
        if local_dt.tzinfo is None:
            local_dt = local_dt.replace(tzinfo=tz)
        return local_dt.astimezone(ZoneInfo("UTC"))
    except KeyError:
        logger.warning(
            "Invalid timezone, assuming UTC",
            timezone=user_timezone
        )
        return local_dt.replace(tzinfo=ZoneInfo("UTC"))


def get_user_today_start(user_timezone: str) -> datetime:
    """Get the start of today (midnight) in user's timezone as UTC.

    Useful for querying "today's" actions in database (which stores UTC).

    Args:
        user_timezone: IANA timezone string

    Returns:
        Start of user's today in UTC
    """
    local_today = get_user_local_date(user_timezone)
    local_midnight = datetime.combine(local_today, datetime.min.time())
    return user_local_to_utc(local_midnight, user_timezone)


def get_user_today_end(user_timezone: str) -> datetime:
    """Get the end of today (23:59:59) in user's timezone as UTC.

    Args:
        user_timezone: IANA timezone string

    Returns:
        End of user's today in UTC
    """
    local_today = get_user_local_date(user_timezone)
    local_end = datetime.combine(local_today, datetime.max.time())
    return user_local_to_utc(local_end, user_timezone)


def format_user_date(
    dt: datetime,
    user_timezone: str,
    format_str: str = "%B %d, %Y"
) -> str:
    """Format a datetime for display in user's timezone.

    Args:
        dt: Datetime to format (UTC or timezone-aware)
        user_timezone: IANA timezone string
        format_str: strftime format string

    Returns:
        Formatted date string in user's timezone
    """
    local_dt = utc_to_user_local(dt, user_timezone)
    return local_dt.strftime(format_str)


def format_user_time(
    dt: datetime,
    user_timezone: str,
    format_str: str = "%I:%M %p"
) -> str:
    """Format a time for display in user's timezone.

    Args:
        dt: Datetime to format (UTC or timezone-aware)
        user_timezone: IANA timezone string
        format_str: strftime format string

    Returns:
        Formatted time string in user's timezone
    """
    local_dt = utc_to_user_local(dt, user_timezone)
    return local_dt.strftime(format_str)


# Common timezone constants for validation
COMMON_TIMEZONES = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Anchorage",
    "Pacific/Honolulu",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Kolkata",
    "Australia/Sydney",
    "Pacific/Auckland",
    "UTC",
]


def is_valid_timezone(timezone: str) -> bool:
    """Check if a timezone string is valid.

    Args:
        timezone: IANA timezone string to validate

    Returns:
        True if valid timezone
    """
    try:
        ZoneInfo(timezone)
        return True
    except KeyError:
        return False
