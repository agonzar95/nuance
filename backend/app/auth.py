"""Authentication utilities for JWT verification.

Provides dependencies for validating Supabase JWT tokens on protected endpoints.
"""

from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, Header
from jwt import PyJWTError
import structlog

from app.config import settings
from app.middleware.error_handler import AuthenticationError

logger = structlog.get_logger()


@dataclass
class User:
    """Authenticated user information extracted from JWT."""

    id: str
    email: str | None = None
    role: str = "authenticated"


def _decode_supabase_jwt(token: str) -> dict[str, str]:
    """Decode and verify a Supabase JWT token.

    Args:
        token: The JWT token string.

    Returns:
        Decoded token payload.

    Raises:
        AuthenticationError: If token is invalid or expired.
    """
    if not settings.supabase_jwt_secret:
        # In development without JWT secret, allow bypass
        if settings.is_development:
            logger.warning("JWT verification skipped - no secret configured")
            return {"sub": "dev-user", "email": "dev@example.com", "role": "authenticated"}
        raise AuthenticationError("JWT secret not configured")

    try:
        payload: dict[str, str] = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except PyJWTError as e:
        logger.warning("JWT decode error", error=str(e))
        raise AuthenticationError("Invalid token")


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None
) -> User:
    """Dependency to extract and validate the current user from JWT.

    Args:
        authorization: The Authorization header value.

    Returns:
        User object with authenticated user information.

    Raises:
        AuthenticationError: If no token or invalid token.
    """
    if not authorization:
        raise AuthenticationError("Authorization header required")

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization format. Use: Bearer <token>")

    token = parts[1]
    payload = _decode_supabase_jwt(token)

    return User(
        id=payload.get("sub", ""),
        email=payload.get("email"),
        role=payload.get("role", "authenticated"),
    )


async def get_optional_user(
    authorization: Annotated[str | None, Header()] = None
) -> User | None:
    """Dependency to optionally extract user from JWT.

    Unlike get_current_user, this returns None if no auth header is present,
    rather than raising an error. Useful for endpoints that work with or
    without authentication.

    Args:
        authorization: The Authorization header value.

    Returns:
        User object if authenticated, None otherwise.
    """
    if not authorization:
        return None

    try:
        return await get_current_user(authorization)
    except AuthenticationError:
        return None


# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
