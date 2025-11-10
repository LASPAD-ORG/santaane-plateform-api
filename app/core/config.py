from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """
    Application settings using Pydantic Settings.
    Automatically loads from environment variables or .env file.

    All configuration variables should be defined in .env file.
    This is the single source of truth for environment configuration.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'  # Ignore extra env vars (e.g., POSTGRES_* used only by docker-compose)
    )

    # Application
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS - Loaded from environment as comma-separated string
    CORS_ORIGINS: str | List[str] = "http://localhost:3000,http://localhost:8080,http://localhost:5173"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Parse CORS_ORIGINS from comma-separated string to list.
        Handles both string (from env) and list (from defaults) formats.
        """
        if isinstance(v, str):
            # Split by comma and strip whitespace from each origin
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v


settings = Settings()
