"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    In development, all fields have defaults to allow running without configuration.
    In production, external service keys should be provided via environment variables.
    """

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""

    # AI Services
    anthropic_api_key: str = ""
    deepgram_api_key: str = ""

    # Telegram
    telegram_bot_token: str = ""
    telegram_secret_token: str = ""

    # Email (Resend)
    resend_api_key: str = ""
    resend_from_email: str = "noreply@example.com"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # Environment
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


settings = Settings()
