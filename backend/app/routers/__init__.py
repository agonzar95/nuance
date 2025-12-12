# API Routers

from app.routers.ai import router as ai_router
from app.routers.transcription import router as transcription_router

__all__ = ["ai_router", "transcription_router"]
