"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    In development, all fields have defaults to allow running without configuration.
    In production/staging, required variables must be set or startup fails fast.
    """

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""  # For verifying user JWTs

    # AI Services
    anthropic_api_key: str = ""
    deepgram_api_key: str = ""

    # Telegram
    telegram_bot_token: str = ""
    telegram_secret_token: str = ""  # Legacy alias for webhook_secret
    telegram_webhook_secret: str = ""  # Secret for verifying webhook requests

    # Application
    app_url: str = "http://localhost:8000"  # Base URL for the app (used for webhooks)

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

    @model_validator(mode="after")
    def validate_required_in_production(self) -> "Settings":
        """Fail fast if required variables are missing in production/staging."""
        if self.environment in ("production", "staging"):
            missing: list[str] = []

            # Core Supabase vars required for auth and data
            if not self.supabase_url:
                missing.append("SUPABASE_URL")
            if not self.supabase_service_key:
                missing.append("SUPABASE_SERVICE_KEY")
            if not self.supabase_jwt_secret:
                missing.append("SUPABASE_JWT_SECRET")

            # AI is core to the product
            if not self.anthropic_api_key:
                missing.append("ANTHROPIC_API_KEY")

            if missing:
                raise ValueError(
                    f"Missing required environment variables for {self.environment}: "
                    f"{', '.join(missing)}"
                )

        return self

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


settings = Settings()
