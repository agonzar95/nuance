"""API client modules for external services."""

from app.clients.supabase import get_client as get_supabase_client
from app.clients.claude import get_claude_client, ClaudeClient
from app.clients.deepgram import get_deepgram_transcriber, DeepgramTranscriber
from app.clients.telegram import get_telegram_client, TelegramClient
from app.clients.resend import get_resend_client, ResendClient

__all__ = [
    "get_supabase_client",
    "get_claude_client",
    "ClaudeClient",
    "get_deepgram_transcriber",
    "DeepgramTranscriber",
    "get_telegram_client",
    "TelegramClient",
    "get_resend_client",
    "ResendClient",
]
