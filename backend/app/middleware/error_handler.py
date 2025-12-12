"""Centralized error handling middleware.

Provides custom exceptions and handlers for consistent error responses.
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError as PydanticValidationError
import structlog

logger = structlog.get_logger()


# ============================================================================
# Error Response Schema
# ============================================================================


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str  # Error code (e.g., "NOT_FOUND", "VALIDATION_ERROR")
    message: str  # Human-readable message
    request_id: str  # Request identifier for tracing
    details: dict[str, Any] | None = None  # Additional error details


# ============================================================================
# Custom Exceptions
# ============================================================================


class AppException(Exception):
    """Base exception for application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None
    ):
        self.message = message or self.__class__.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found."""
    status_code = 404
    error_code = "NOT_FOUND"
    message = "Resource not found"


class ValidationError(AppException):
    """Request validation failed."""
    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "Validation failed"


class AuthenticationError(AppException):
    """Authentication required or failed."""
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"
    message = "Authentication required"


class AuthorizationError(AppException):
    """Insufficient permissions."""
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"
    message = "Permission denied"


class ExternalServiceError(AppException):
    """External service (API, database) failure."""
    status_code = 502
    error_code = "EXTERNAL_SERVICE_ERROR"
    message = "External service unavailable"


# ============================================================================
# Exception Handlers
# ============================================================================


def get_request_id(request: Request) -> str:
    """Extract request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle custom application exceptions."""
    request_id = get_request_id(request)

    # Cast to AppException (we know it is one since this handler is registered for AppException)
    app_exc = exc if isinstance(exc, AppException) else AppException(str(exc))

    logger.warning(
        "Application error",
        error_code=app_exc.error_code,
        message=app_exc.message,
        status_code=app_exc.status_code,
        details=app_exc.details,
    )

    return JSONResponse(
        status_code=app_exc.status_code,
        content=ErrorResponse(
            error=app_exc.error_code,
            message=app_exc.message,
            request_id=request_id,
            details=app_exc.details,
        ).model_dump(),
    )


async def pydantic_validation_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    request_id = get_request_id(request)

    # Cast to PydanticValidationError
    validation_exc = exc if isinstance(exc, PydanticValidationError) else None
    errors = validation_exc.errors() if validation_exc else []
    details = {
        "validation_errors": [
            {
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", ""),
                "type": err.get("type", ""),
            }
            for err in errors
        ]
    }

    logger.warning(
        "Validation error",
        error_count=len(errors),
        details=details,
    )

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message="Request validation failed",
            request_id=request_id,
            details=details,
        ).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions.

    Logs the full stack trace but returns sanitized error to client.
    """
    request_id = get_request_id(request)

    # Log full exception with stack trace
    logger.exception(
        "Unhandled error",
        error_type=type(exc).__name__,
        error_message=str(exc),
    )

    # Return sanitized error (no internal details exposed)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="An unexpected error occurred",
            request_id=request_id,
            details=None,
        ).model_dump(),
    )


# ============================================================================
# Setup Function
# ============================================================================


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance.
    """
    # Custom application exceptions
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(NotFoundError, app_exception_handler)
    app.add_exception_handler(ValidationError, app_exception_handler)
    app.add_exception_handler(AuthenticationError, app_exception_handler)
    app.add_exception_handler(AuthorizationError, app_exception_handler)
    app.add_exception_handler(ExternalServiceError, app_exception_handler)

    # Pydantic validation errors
    app.add_exception_handler(PydanticValidationError, pydantic_validation_handler)

    # Catch-all for unhandled exceptions
    app.add_exception_handler(Exception, generic_exception_handler)
