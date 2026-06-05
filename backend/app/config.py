"""
Application configuration — reads from .env file.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/greenhouse_intelligence"

    # ML Model paths (relative to backend/ directory)
    MODEL_DIR: str = "../models"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def model_dir_abs(self) -> str:
        """Return absolute path to models directory."""
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.normpath(os.path.join(backend_dir, self.MODEL_DIR))

    class Config:
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
        )
        extra = "ignore"


settings = Settings()
