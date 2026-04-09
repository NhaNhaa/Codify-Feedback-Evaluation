"""Unit tests for application configuration."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.app.config import Settings


def test_settings_loads_valid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings parses correctly when all required env vars are present."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key-123")

    settings = Settings()

    assert settings.groq_api_key == "test-key-123"


def test_settings_default_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default model is llama-3.3-70b-versatile when not explicitly set."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key-123")

    settings = Settings()

    assert settings.groq_model == "llama-3.3-70b-versatile"


def test_settings_default_data_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default data_dir is 'data' when not explicitly set."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key-123")

    settings = Settings()

    assert settings.data_dir == "data"


def test_settings_raises_when_api_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings raises ValidationError when GROQ_API_KEY is absent."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_custom_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings respects custom env var overrides."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key-123")
    monkeypatch.setenv("GROQ_MODEL", "llama3-8b-8192")
    monkeypatch.setenv("DATA_DIR", "custom_data")

    settings = Settings()

    assert settings.groq_model == "llama3-8b-8192"
    assert settings.data_dir == "custom_data"