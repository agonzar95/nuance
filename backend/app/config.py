"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""

    # AI Services
    anthropic_api_key: str = ""
    deepgram_api_key: str = ""

    # Telegram
    telegram_bot_token: str = ""
    telegram_secret_token: str = ""

    # Email
    resend_api_key: str = ""

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # Environment
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
