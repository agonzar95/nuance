"""Prompt versioning and management.

This module provides versioned prompts for AI operations. All prompts
are registered in a central registry and can be retrieved by name.

Usage:
    from app.prompts import get_prompt

    extraction_prompt = get_prompt("extraction")
    formatted = extraction_prompt.format(text="user input")
"""

from app.prompts.registry import (
    PromptRegistry,
    PromptVersion,
    get_prompt,
    get_prompt_registry,
)

__all__ = [
    "PromptRegistry",
    "PromptVersion",
    "get_prompt",
    "get_prompt_registry",
]
