# API Routers

from app.routers.ai import router as ai_router
from app.routers.transcription import router as transcription_router
from app.routers.telegram import router as telegram_router
from app.routers.knowledge import router as knowledge_router

__all__ = ["ai_router", "transcription_router", "telegram_router", "knowledge_router"]
