"""Application configuration and environment variables."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the backend/app directory (2 levels up from this file)
# File is at: backend/app/core/config.py
# We need to go up 2 levels to reach the backend/app directory
BACKEND_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    PROJECT_NAME: str = "Speaking Practice App"
    API_V1_STR: str = "/api/v1"

    # Data Settings
    DATA_DIR: str = os.path.join(BACKEND_APP_DIR, "data")

    # Audio Settings
    AUDIO_UPLOAD_DIR: str = os.path.join(DATA_DIR, "uploads")
    AUDIO_OUTPUT_DIR: str = os.path.join(DATA_DIR, "outputs")

    # LLM Settings - Supports any OpenAI-compatible API
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")

    # Model Config
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# Ensure directories exist
os.makedirs(settings.AUDIO_UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_OUTPUT_DIR, exist_ok=True)
