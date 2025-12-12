"""Transcription API endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
import structlog

from app.services.transcription import TranscriptionService, get_transcription_service

logger = structlog.get_logger()

router = APIRouter(prefix="/transcribe", tags=["transcription"])


class TranscriptionResponse(BaseModel):
    """Response model for transcription endpoints."""
    text: str


class TelegramVoiceRequest(BaseModel):
    """Request model for Telegram voice transcription."""
    file_id: str


def get_service() -> TranscriptionService:
    """Dependency: Get transcription service without Telegram."""
    return get_transcription_service(with_telegram=False)


def get_service_with_telegram() -> TranscriptionService:
    """Dependency: Get transcription service with Telegram support."""
    return get_transcription_service(with_telegram=True)


@router.post("", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    service: TranscriptionService = Depends(get_service),
) -> TranscriptionResponse:
    """Transcribe uploaded audio file.

    Accepts audio in common formats (webm, ogg, mp3, wav).

    Args:
        audio: Uploaded audio file.
        service: Injected transcription service.

    Returns:
        Transcribed text.
    """
    # Read audio bytes
    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # Determine mimetype
    mimetype = audio.content_type or "audio/webm"

    logger.info(
        "Transcription request",
        filename=audio.filename,
        mimetype=mimetype,
        size=len(audio_bytes)
    )

    try:
        text = await service.transcribe_bytes(audio_bytes, mimetype)
        return TranscriptionResponse(text=text)
    except Exception as e:
        logger.error("Transcription failed", error=str(e))
        raise HTTPException(status_code=500, detail="Transcription failed")


@router.post("/telegram", response_model=TranscriptionResponse)
async def transcribe_telegram_voice(
    request: TelegramVoiceRequest,
    service: TranscriptionService = Depends(get_service_with_telegram),
) -> TranscriptionResponse:
    """Transcribe a Telegram voice note by file_id.

    Downloads the voice note from Telegram and transcribes it.

    Args:
        request: Request containing Telegram file_id.
        service: Injected transcription service with Telegram support.

    Returns:
        Transcribed text.
    """
    logger.info("Telegram transcription request", file_id=request.file_id)

    try:
        text = await service.transcribe_telegram_voice(request.file_id)
        return TranscriptionResponse(text=text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Telegram transcription failed", error=str(e))
        raise HTTPException(status_code=500, detail="Transcription failed")
