"""AI Provider abstraction layer.

This module provides an abstract interface for AI completions that can be
implemented by different providers. Currently supports Claude, with the
architecture designed to easily add other providers in the future.

Usage:
    from app.ai import get_ai_provider, AIProvider

    provider = get_ai_provider()
    response = await provider.complete(messages)

The factory function returns the configured provider based on application
settings. All code should use the abstract AIProvider interface rather
than concrete implementations for easier testing and provider swapping.
"""

from app.ai.base import AIProvider, CompletionResponse, Message
from app.ai.claude import ClaudeProvider


def get_ai_provider() -> AIProvider:
    """Factory function to get the configured AI provider.

    Returns:
        AIProvider instance based on configuration.

    Currently always returns ClaudeProvider. In the future, this could
    read from settings to determine which provider to use.
    """
    return ClaudeProvider()


__all__ = [
    "AIProvider",
    "ClaudeProvider",
    "CompletionResponse",
    "Message",
    "get_ai_provider",
]
