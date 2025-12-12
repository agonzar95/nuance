"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application.

    In development: Human-readable colored output
    In production: JSON output for log aggregation
    """
    # Common processors for all environments
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.is_development:
        # Development: colored, human-readable output
        processors: list[Processor] = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to work with structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Logger name, typically __name__ of the module.

    Returns:
        Configured structlog logger.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("User action", user_id="123", action="login")
    """
    return structlog.get_logger(name)


def bind_request_context(**kwargs: Any) -> None:
    """Bind context variables to all subsequent log calls.

    Typically called at the start of request handling to add
    request_id and user_id to all logs within that request.

    Args:
        **kwargs: Key-value pairs to bind to log context.

    Example:
        >>> bind_request_context(request_id="abc-123", user_id="user-456")
        >>> logger.info("Processing")  # Will include request_id and user_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_request_context() -> None:
    """Clear all bound context variables.

    Typically called at the end of request handling.
    """
    structlog.contextvars.clear_contextvars()
