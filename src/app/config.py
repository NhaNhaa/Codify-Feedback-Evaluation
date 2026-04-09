"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """All runtime configuration for Codify.

    Values are loaded from environment variables or a .env file.
    Never hardcode secrets — see .env.example for required variables.
    """

    groq_api_key: str = Field(..., description="Groq API key")
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model identifier",
    )
    data_dir: str = Field(default="data", description="Root dir for JSON persistence")
    chroma_path: str = Field(
        default="data/chroma",
        description="ChromaDB embedded storage path",
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Return a Settings instance loaded from environment.

    Returns:
        Settings: Validated application configuration.

    Raises:
        ValidationError: If any required environment variable is missing.
    """
    return Settings()