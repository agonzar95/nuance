"""Claude AI provider implementation.

Implements the AIProvider interface using Anthropic's Claude API.
"""

import asyncio
import json
from collections.abc import AsyncIterator
from typing import TypeVar

from anthropic import Anthropic, APIError, RateLimitError
from pydantic import BaseModel
import structlog

from app.ai.base import AIProvider, CompletionResponse, Message
from app.config import settings

logger = structlog.get_logger()

T = TypeVar("T", bound=BaseModel)


class ClaudeProvider(AIProvider):
    """Claude implementation of AIProvider.

    Uses Anthropic's Claude API for completions, streaming, and extraction.
    Includes retry logic for rate limits and robust error handling.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        max_retries: int = 3,
    ):
        """Initialize Claude provider.

        Args:
            api_key: Anthropic API key. Defaults to settings value.
            model: Model identifier to use.
            max_retries: Maximum retry attempts for rate limits.
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("Anthropic API key must be configured")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_retries = max_retries

    def _messages_to_api_format(self, messages: list[Message]) -> list[dict[str, str]]:
        """Convert Message objects to API format."""
        return [{"role": m.role, "content": m.content} for m in messages]

    async def complete(
        self,
        messages: list[Message],
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> CompletionResponse:
        """Generate a completion using Claude.

        Implements retry logic for rate limits and returns token usage.
        """
        api_messages = self._messages_to_api_format(messages)
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                # Run sync API call in thread pool
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        system=system or "",
                        messages=api_messages,
                    ),
                )

                text_block = response.content[0]
                content = str(getattr(text_block, "text", ""))

                return CompletionResponse(
                    content=content,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                )
            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    logger.warning(
                        "Rate limited, retrying",
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                    )
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            except APIError as e:
                logger.error("Claude API error", error=str(e))
                raise

        raise last_error or APIError(message="Max retries exceeded")

    async def stream(
        self,
        messages: list[Message],
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Stream a completion from Claude.

        Yields text chunks as they are generated. Note: The Anthropic SDK
        uses sync streaming, so we run it in a thread pool for async support.
        """
        api_messages = self._messages_to_api_format(messages)

        def sync_stream() -> list[str]:
            """Run sync streaming and collect chunks."""
            chunks = []
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system or "",
                messages=api_messages,
            ) as stream:
                for text in stream.text_stream:
                    chunks.append(text)
            return chunks

        # Run sync streaming in thread pool and yield results
        loop = asyncio.get_event_loop()
        chunks = await loop.run_in_executor(None, sync_stream)

        for chunk in chunks:
            yield chunk

    async def extract(
        self,
        text: str,
        schema: type[T],
        system: str,
    ) -> T:
        """Extract structured data from text using Claude.

        Uses JSON mode with schema validation to extract structured data.
        """
        extraction_prompt = f"""{system}

Output your response as valid JSON matching this schema:
{json.dumps(schema.model_json_schema(), indent=2)}

Text to extract from:
{text}

Respond with only the JSON object, no other text."""

        response = await self.complete(
            messages=[Message(role="user", content=extraction_prompt)],
            max_tokens=2048,
        )

        # Parse the JSON response
        try:
            json_str = response.content.strip()
            # Handle potential markdown code blocks
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
                response=response.content[:200],
                error=str(e),
            )
            raise ValueError(f"Failed to extract structured data: {e}")
