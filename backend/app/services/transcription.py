"""Voice transcription service.

Unified service handling both web audio and Telegram voice messages.
"""

import structlog

from app.clients.deepgram import DeepgramTranscriber, get_deepgram_transcriber
from app.clients.telegram import TelegramClient, get_telegram_client

logger = structlog.get_logger()


class TranscriptionService:
    """Unified voice transcription service.

    Handles transcription from multiple sources:
    - Raw audio bytes (from web MediaRecorder)
    - Telegram voice notes (downloaded via file_id)
    """

    def __init__(
        self,
        deepgram: DeepgramTranscriber | None = None,
        telegram: TelegramClient | None = None,
    ):
        """Initialize the transcription service.

        Args:
            deepgram: Deepgram transcriber client. Defaults to auto-configured.
            telegram: Telegram client for voice note downloads. Optional.
        """
        self.deepgram = deepgram or get_deepgram_transcriber()
        self.telegram = telegram

    async def transcribe_bytes(
        self,
        audio: bytes,
        mimetype: str = "audio/webm"
    ) -> str:
        """Transcribe raw audio bytes.

        Args:
            audio: Raw audio data.
            mimetype: MIME type of audio (webm, ogg, mp3, etc.).

        Returns:
            Transcribed text.

        Raises:
            ValueError: If audio is empty.
            Exception: If transcription fails.
        """
        if not audio:
            raise ValueError("Audio data cannot be empty")

        logger.info(
            "Transcribing audio bytes",
            size=len(audio),
            mimetype=mimetype
        )

        return await self.deepgram.transcribe(audio, mimetype)

    async def transcribe_telegram_voice(self, file_id: str) -> str:
        """Download and transcribe a Telegram voice note.

        Args:
            file_id: Telegram file identifier for the voice note.

        Returns:
            Transcribed text.

        Raises:
            ValueError: If Telegram client not configured.
            Exception: If download or transcription fails.
        """
        if not self.telegram:
            raise ValueError("Telegram client not configured for voice transcription")

        logger.info("Transcribing Telegram voice", file_id=file_id)

        # Download voice note from Telegram
        audio_bytes = await self.telegram.get_file(file_id)

        # Telegram voice notes are typically OGG/OPUS format
        return await self.deepgram.transcribe(audio_bytes, mimetype="audio/ogg")


# Factory function for dependency injection
def get_transcription_service(
    with_telegram: bool = False
) -> TranscriptionService:
    """Get a configured transcription service.

    Args:
        with_telegram: Include Telegram client for voice note support.

    Returns:
        Configured TranscriptionService instance.
    """
    telegram = get_telegram_client() if with_telegram else None
    return TranscriptionService(telegram=telegram)
