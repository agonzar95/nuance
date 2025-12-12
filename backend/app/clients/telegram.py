"""Telegram Bot API client."""

from typing import Any

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()


class TelegramClient:
    """Client wrapper for Telegram Bot API."""

    def __init__(self, bot_token: str | None = None):
        """Initialize Telegram client.

        Args:
            bot_token: Telegram bot token. Defaults to settings value.
        """
        self.token = bot_token or settings.telegram_bot_token
        if not self.token:
            raise ValueError("Telegram bot token must be configured")

        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.file_url = f"https://api.telegram.org/file/bot{self.token}"
        self._http: httpx.AsyncClient | None = None

    async def _get_http(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=30.0)
        return self._http

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str = "Markdown"
    ) -> bool:
        """Send a text message to a chat.

        Args:
            chat_id: Telegram chat ID.
            text: Message text.
            parse_mode: Message formatting (Markdown, HTML, or empty).

        Returns:
            True if message was sent successfully.
        """
        http = await self._get_http()

        try:
            response = await http.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }
            )
            result: dict[str, Any] = response.json()

            if result.get("ok"):
                logger.info("Message sent", chat_id=chat_id)
                return True
            else:
                logger.warning(
                    "Message send failed",
                    chat_id=chat_id,
                    error=result.get("description")
                )
                return False

        except Exception as e:
            logger.error("Telegram API error", error=str(e))
            return False

    async def get_file(self, file_id: str) -> bytes:
        """Download a file by file_id (for voice notes).

        Args:
            file_id: Telegram file identifier.

        Returns:
            File contents as bytes.

        Raises:
            Exception: If download fails.
        """
        http = await self._get_http()

        # Get file path
        response = await http.get(
            f"{self.base_url}/getFile",
            params={"file_id": file_id}
        )
        result: dict[str, Any] = response.json()

        if not result.get("ok"):
            raise Exception(f"Failed to get file info: {result.get('description')}")

        file_path: str = result["result"]["file_path"]

        # Download file
        file_response = await http.get(f"{self.file_url}/{file_path}")

        if file_response.status_code != 200:
            raise Exception(f"Failed to download file: {file_response.status_code}")

        logger.info("File downloaded", file_id=file_id, size=len(file_response.content))
        return file_response.content

    async def set_webhook(self, url: str, secret_token: str | None = None) -> bool:
        """Set webhook URL for receiving updates.

        Args:
            url: HTTPS URL for webhook.
            secret_token: Optional secret token for webhook verification.

        Returns:
            True if webhook was set successfully.
        """
        http = await self._get_http()

        payload: dict[str, str] = {"url": url}
        if secret_token:
            payload["secret_token"] = secret_token

        try:
            response = await http.post(
                f"{self.base_url}/setWebhook",
                json=payload
            )
            result: dict[str, Any] = response.json()

            if result.get("ok"):
                logger.info("Webhook set", url=url)
                return True
            else:
                logger.error(
                    "Webhook set failed",
                    error=result.get("description")
                )
                return False

        except Exception as e:
            logger.error("Failed to set webhook", error=str(e))
            return False

    async def delete_webhook(self) -> bool:
        """Remove the current webhook.

        Returns:
            True if webhook was deleted successfully.
        """
        http = await self._get_http()

        try:
            response = await http.post(f"{self.base_url}/deleteWebhook")
            result: dict[str, Any] = response.json()
            return bool(result.get("ok", False))
        except Exception as e:
            logger.error("Failed to delete webhook", error=str(e))
            return False


# Factory function for dependency injection
def get_telegram_client() -> TelegramClient:
    """Get a configured Telegram client instance."""
    return TelegramClient()
