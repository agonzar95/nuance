"""Claude API client wrapper with retry logic and structured extraction."""

import json
from collections.abc import Iterator
from typing import Any, TypeVar

from anthropic import Anthropic, APIError, RateLimitError
from pydantic import BaseModel
import structlog

from app.config import settings

logger = structlog.get_logger()

T = TypeVar("T", bound=BaseModel)


class ClaudeClient:
    """Client wrapper for Claude API with error handling and structured output."""

    def __init__(self, api_key: str | None = None):
        """Initialize Claude client.

        Args:
            api_key: Anthropic API key. Defaults to settings value.
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("Anthropic API key must be configured")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_retries = 3

    def chat(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
        max_tokens: int = 1024
    ) -> str:
        """Send a chat message and get a response.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            system: Optional system prompt.
            max_tokens: Maximum tokens in response.

        Returns:
            The assistant's response text.

        Raises:
            APIError: If the API request fails after retries.
        """
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system or "",
                    messages=messages
                )
                text_block = response.content[0]
                return str(getattr(text_block, "text", ""))
            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    logger.warning(
                        "Rate limited, retrying",
                        attempt=attempt + 1,
                        max_retries=self.max_retries
                    )
                    continue
                raise
            except APIError as e:
                logger.error("Claude API error", error=str(e))
                raise
        # This should not be reached but satisfies mypy
        raise last_error or APIError("Max retries exceeded")

    def chat_stream(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
        max_tokens: int = 1024
    ) -> Iterator[str]:
        """Stream a chat response.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            system: Optional system prompt.
            max_tokens: Maximum tokens in response.

        Yields:
            Text chunks as they arrive.
        """
        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system or "",
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                yield text

    def extract(
        self,
        text: str,
        schema: type[T],
        system: str
    ) -> T:
        """Extract structured data from text using a Pydantic schema.

        Args:
            text: The text to extract from.
            schema: Pydantic model class defining the expected structure.
            system: System prompt guiding the extraction.

        Returns:
            Parsed Pydantic model instance.

        Raises:
            ValueError: If extraction fails to produce valid JSON.
        """
        extraction_prompt = f"""{system}

Output your response as valid JSON matching this schema:
{json.dumps(schema.model_json_schema(), indent=2)}

Text to extract from:
{text}

Respond with only the JSON object, no other text."""

        response = self.chat(
            messages=[{"role": "user", "content": extraction_prompt}],
            max_tokens=2048
        )

        # Parse the JSON response
        try:
            # Handle potential markdown code blocks
            json_str = response.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
            json_str = json_str.strip()

            data = json.loads(json_str)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                "Failed to parse extraction response",
                response=response[:200],
                error=str(e)
            )
            raise ValueError(f"Failed to extract structured data: {e}")


# Factory function for dependency injection
def get_claude_client() -> ClaudeClient:
    """Get a configured Claude client instance."""
    return ClaudeClient()
