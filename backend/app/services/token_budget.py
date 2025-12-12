"""Token budget service for tracking and limiting AI usage.

Tracks input and output tokens per API call, maintains daily budgets,
and provides warnings/blocking when limits are approached/exceeded.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from typing import Any

import structlog

from app.clients.supabase import get_client

logger = structlog.get_logger()


@dataclass
class TokenUsage:
    """Token usage for a single AI call."""

    input_tokens: int
    output_tokens: int
    endpoint: str | None = None

    @property
    def total(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens


@dataclass
class BudgetStatus:
    """Current budget status for a user."""

    used_today: int
    daily_limit: int
    percentage_used: float
    has_budget: bool
    warning: bool  # True if > 80% used
    tokens_remaining: int


class TokenBudgetService:
    """Service for tracking and enforcing token budgets.

    Each user has a daily token budget (default 100K tokens).
    Provides warnings at 80% usage and blocks at 100%.
    """

    DEFAULT_DAILY_LIMIT = 100_000
    WARNING_THRESHOLD = 0.8  # 80%

    def __init__(self, daily_limit: int | None = None):
        """Initialize token budget service.

        Args:
            daily_limit: Override default daily token limit.
        """
        self.daily_limit = daily_limit or self.DEFAULT_DAILY_LIMIT

    async def check_budget(self, user_id: str) -> BudgetStatus:
        """Check if user has remaining token budget.

        Args:
            user_id: The user's ID.

        Returns:
            BudgetStatus with current usage and availability.
        """
        used_today = await self._get_today_usage(user_id)
        percentage = used_today / self.daily_limit
        has_budget = percentage < 1.0
        warning = percentage >= self.WARNING_THRESHOLD

        return BudgetStatus(
            used_today=used_today,
            daily_limit=self.daily_limit,
            percentage_used=round(percentage, 3),
            has_budget=has_budget,
            warning=warning,
            tokens_remaining=max(0, self.daily_limit - used_today),
        )

    async def record_usage(
        self,
        user_id: str,
        usage: TokenUsage,
    ) -> None:
        """Record token usage for a user.

        Args:
            user_id: The user's ID.
            usage: Token usage details.
        """
        try:
            client = get_client()

            data = {
                "user_id": user_id,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "endpoint": usage.endpoint,
                "created_at": datetime.now(UTC).isoformat(),
            }

            client.table("token_usage").insert(data).execute()

            logger.debug(
                "Token usage recorded",
                user_id=user_id,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                total=usage.total,
            )
        except Exception as e:
            # Don't let recording failures break the main flow
            logger.error("Failed to record token usage", error=str(e))

    async def _get_today_usage(self, user_id: str) -> int:
        """Get total tokens used today by user.

        Args:
            user_id: The user's ID.

        Returns:
            Total tokens used today (input + output).
        """
        try:
            client = get_client()

            # Get start of today in UTC
            today_start = datetime.now(UTC).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            result = client.table("token_usage").select(
                "input_tokens, output_tokens"
            ).eq("user_id", user_id).gte(
                "created_at", today_start.isoformat()
            ).execute()

            if not result.data:
                return 0

            total: int = sum(
                int(row.get("input_tokens", 0)) + int(row.get("output_tokens", 0))
                for row in result.data
            )
            return total
        except Exception as e:
            logger.error("Failed to get token usage", error=str(e))
            return 0

    async def get_usage_stats(
        self,
        user_id: str,
        days: int = 7,
    ) -> dict[str, Any]:
        """Get token usage statistics for a user.

        Args:
            user_id: The user's ID.
            days: Number of days to look back.

        Returns:
            Dict with usage statistics.
        """
        try:
            client = get_client()

            start_date = datetime.now(UTC) - timedelta(days=days)

            result = client.table("token_usage").select(
                "input_tokens, output_tokens, endpoint, created_at"
            ).eq("user_id", user_id).gte(
                "created_at", start_date.isoformat()
            ).execute()

            if not result.data:
                return {
                    "total_tokens": 0,
                    "total_requests": 0,
                    "by_endpoint": {},
                    "daily_average": 0,
                }

            total_tokens = sum(
                row.get("input_tokens", 0) + row.get("output_tokens", 0)
                for row in result.data
            )

            # Group by endpoint
            by_endpoint: dict[str, int] = {}
            for row in result.data:
                endpoint = row.get("endpoint") or "unknown"
                tokens = row.get("input_tokens", 0) + row.get("output_tokens", 0)
                by_endpoint[endpoint] = by_endpoint.get(endpoint, 0) + tokens

            return {
                "total_tokens": total_tokens,
                "total_requests": len(result.data),
                "by_endpoint": by_endpoint,
                "daily_average": total_tokens // days if days > 0 else 0,
            }
        except Exception as e:
            logger.error("Failed to get usage stats", error=str(e))
            return {
                "total_tokens": 0,
                "total_requests": 0,
                "by_endpoint": {},
                "daily_average": 0,
            }


# Global service instance
_token_budget_service: TokenBudgetService | None = None


def get_token_budget_service() -> TokenBudgetService:
    """Get or create the token budget service instance."""
    global _token_budget_service
    if _token_budget_service is None:
        _token_budget_service = TokenBudgetService()
    return _token_budget_service
