"""Rate limiting utilities for AI endpoints.

Implements per-user rate limiting with configurable limits for
requests per minute and per day.
"""

from collections import defaultdict
from datetime import datetime, timedelta, UTC
from typing import NamedTuple

import structlog

logger = structlog.get_logger()


class RateLimitResult(NamedTuple):
    """Result of a rate limit check."""

    allowed: bool
    retry_after_seconds: int | None = None
    requests_remaining: int = 0
    limit_type: str | None = None  # 'minute' or 'day'


class RateLimiter:
    """In-memory rate limiter with per-minute and per-day limits.

    For production, consider using Redis for distributed rate limiting
    across multiple server instances.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_day: int = 500,
    ):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute.
            requests_per_day: Maximum requests allowed per day.
        """
        self.rpm = requests_per_minute
        self.rpd = requests_per_day

        # Track request timestamps per user for minute window
        self.minute_requests: dict[str, list[datetime]] = defaultdict(list)

        # Track daily counts per user
        self.day_counts: dict[str, int] = defaultdict(int)
        self.day_reset: dict[str, datetime] = {}

    def _clean_minute_window(self, user_id: str, now: datetime) -> None:
        """Remove requests older than 1 minute."""
        minute_ago = now - timedelta(minutes=1)
        self.minute_requests[user_id] = [
            t for t in self.minute_requests[user_id] if t > minute_ago
        ]

    def _check_day_reset(self, user_id: str, now: datetime) -> None:
        """Reset daily count if it's a new day."""
        if user_id in self.day_reset:
            last_reset = self.day_reset[user_id]
            if now.date() > last_reset.date():
                self.day_counts[user_id] = 0
                self.day_reset[user_id] = now
        else:
            self.day_reset[user_id] = now

    def _seconds_until_midnight(self, now: datetime) -> int:
        """Calculate seconds until midnight UTC."""
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return int((tomorrow - now).total_seconds())

    def check(self, user_id: str) -> RateLimitResult:
        """Check if a request is allowed for the given user.

        Args:
            user_id: The user's unique identifier.

        Returns:
            RateLimitResult with allowed status and retry info.
        """
        now = datetime.now(UTC)

        # Clean old minute window entries
        self._clean_minute_window(user_id, now)

        # Check day reset
        self._check_day_reset(user_id, now)

        # Check minute limit
        minute_count = len(self.minute_requests[user_id])
        if minute_count >= self.rpm:
            oldest = min(self.minute_requests[user_id])
            retry_after = 60 - int((now - oldest).total_seconds())
            retry_after = max(1, retry_after)  # At least 1 second

            logger.warning(
                "Rate limit exceeded (minute)",
                user_id=user_id,
                count=minute_count,
                limit=self.rpm,
            )

            return RateLimitResult(
                allowed=False,
                retry_after_seconds=retry_after,
                requests_remaining=0,
                limit_type="minute",
            )

        # Check daily limit
        day_count = self.day_counts[user_id]
        if day_count >= self.rpd:
            retry_after = self._seconds_until_midnight(now)

            logger.warning(
                "Rate limit exceeded (day)",
                user_id=user_id,
                count=day_count,
                limit=self.rpd,
            )

            return RateLimitResult(
                allowed=False,
                retry_after_seconds=retry_after,
                requests_remaining=0,
                limit_type="day",
            )

        # Request allowed - record it
        self.minute_requests[user_id].append(now)
        self.day_counts[user_id] += 1

        # Calculate remaining requests (use the more restrictive limit)
        minute_remaining = self.rpm - len(self.minute_requests[user_id])
        day_remaining = self.rpd - self.day_counts[user_id]
        remaining = min(minute_remaining, day_remaining)

        return RateLimitResult(
            allowed=True,
            retry_after_seconds=None,
            requests_remaining=remaining,
        )

    def get_status(self, user_id: str) -> dict[str, int]:
        """Get current rate limit status for a user.

        Args:
            user_id: The user's unique identifier.

        Returns:
            Dict with current usage counts.
        """
        now = datetime.now(UTC)
        self._clean_minute_window(user_id, now)
        self._check_day_reset(user_id, now)

        return {
            "minute_count": len(self.minute_requests[user_id]),
            "minute_limit": self.rpm,
            "minute_remaining": self.rpm - len(self.minute_requests[user_id]),
            "day_count": self.day_counts[user_id],
            "day_limit": self.rpd,
            "day_remaining": self.rpd - self.day_counts[user_id],
        }


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
