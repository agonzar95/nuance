"""Supabase client for backend admin operations."""

from supabase import create_client, Client

from app.config import settings


def get_supabase_client() -> Client:
    """Create and return a Supabase client with service role key.

    The service role key bypasses Row Level Security (RLS) for admin operations.
    Use with caution and only for operations that require elevated privileges.
    """
    if not settings.supabase_url or not settings.supabase_service_key:
        raise ValueError("Supabase URL and service key must be configured")

    return create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )


# Singleton client for reuse
_client: Client | None = None


def get_client() -> Client:
    """Get or create the singleton Supabase client."""
    global _client
    if _client is None:
        _client = get_supabase_client()
    return _client
