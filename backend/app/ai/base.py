"""Abstract AI provider interface.

Defines a common interface for AI completions that can be implemented by
different providers (Claude, OpenAI, etc.). This abstraction allows
swapping providers without changing application code.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TypeVar

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a conversation."""

    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")


class CompletionResponse(BaseModel):
    """Response from a completion request."""

    content: str = Field(..., description="Generated text content")
    input_tokens: int = Field(..., ge=0, description="Number of input tokens")
    output_tokens: int = Field(..., ge=0, description="Number of output tokens")

    @property
    def total_tokens(self) -> int:
        """Total tokens used in this completion."""
        return self.input_tokens + self.output_tokens


T = TypeVar("T", bound=BaseModel)


class AIProvider(ABC):
    """Abstract base class for AI providers.

    Implementations must provide methods for:
    - complete: Single-turn completion
    - stream: Streaming completion
    - extract: Structured extraction using Pydantic models
    """

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> CompletionResponse:
        """Generate a completion for the given messages.

        Args:
            messages: List of conversation messages.
            system: Optional system prompt.
            max_tokens: Maximum tokens to generate.

        Returns:
            CompletionResponse with generated content and token usage.
        """
        ...

    @abstractmethod
    def stream(
        self,
        messages: list[Message],
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Stream a completion for the given messages.

        Args:
            messages: List of conversation messages.
            system: Optional system prompt.
            max_tokens: Maximum tokens to generate.

        Yields:
            Text chunks as they are generated.
        """
        ...

    @abstractmethod
    async def extract(
        self,
        text: str,
        schema: type[T],
        system: str,
    ) -> T:
        """Extract structured data from text using a Pydantic schema.

        Args:
            text: The text to extract from.
            schema: Pydantic model class defining the expected structure.
            system: System prompt guiding the extraction.

        Returns:
            Parsed Pydantic model instance.

        Raises:
            ValueError: If extraction fails to produce valid data.
        """
        ...
