"""Deepgram client for voice transcription."""

from typing import Any

from deepgram import DeepgramClient, PrerecordedOptions
import structlog

from app.config import settings

logger = structlog.get_logger()


class DeepgramTranscriber:
    """Client wrapper for Deepgram transcription API."""

    def __init__(self, api_key: str | None = None):
        """Initialize Deepgram client.

        Args:
            api_key: Deepgram API key. Defaults to settings value.
        """
        self.api_key = api_key or settings.deepgram_api_key
        if not self.api_key:
            raise ValueError("Deepgram API key must be configured")

        self.client = DeepgramClient(self.api_key)
        self.options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            punctuate=True,
            language="en"
        )

    async def transcribe(self, audio_bytes: bytes, mimetype: str = "audio/webm") -> str:
        """Transcribe audio bytes to text.

        Args:
            audio_bytes: Raw audio data.
            mimetype: MIME type of the audio (e.g., 'audio/webm', 'audio/ogg').

        Returns:
            Transcribed text.

        Raises:
            Exception: If transcription fails.
        """
        try:
            response: Any = await self.client.listen.asyncrest.v("1").transcribe_file(
                {"buffer": audio_bytes, "mimetype": mimetype},
                self.options
            )

            # Extract transcript from response
            transcript: str = response.results.channels[0].alternatives[0].transcript

            logger.info(
                "Transcription complete",
                length=len(transcript),
                words=len(transcript.split())
            )

            return transcript

        except Exception as e:
            logger.error("Transcription failed", error=str(e))
            raise

    async def transcribe_url(self, audio_url: str) -> str:
        """Transcribe audio from a URL.

        Args:
            audio_url: URL to the audio file.

        Returns:
            Transcribed text.
        """
        try:
            response: Any = await self.client.listen.asyncrest.v("1").transcribe_url(
                {"url": audio_url},
                self.options
            )

            transcript: str = response.results.channels[0].alternatives[0].transcript

            logger.info(
                "URL transcription complete",
                length=len(transcript)
            )

            return transcript

        except Exception as e:
            logger.error("URL transcription failed", error=str(e), url=audio_url)
            raise


# Factory function for dependency injection
def get_deepgram_transcriber() -> DeepgramTranscriber:
    """Get a configured Deepgram transcriber instance."""
    return DeepgramTranscriber()
