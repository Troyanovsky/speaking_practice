"""Pydantic schemas for user settings and configuration.

This module defines schemas for:
- User language and proficiency settings
- LLM API configuration
- TTS speed settings
- Settings validation with field validators
"""

from typing import Optional

from pydantic import BaseModel, field_validator

from app.services.tts_service import LANGUAGE_CONFIG


class UserSettings(BaseModel):
    """User configuration settings for the practice app."""

    primary_language: str = "English"
    target_language: str = "Spanish"
    proficiency_level: str = "A1"
    stop_word: str = "stop session"

    # TTS Settings
    tts_speed: float = 1.0

    # LLM Settings
    llm_base_url: Optional[str] = "https://api.openai.com/v1"
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = "gpt-4o"

    @field_validator("tts_speed")
    @classmethod
    def validate_tts_speed(cls, v: float) -> float:
        """Validate TTS speed is within acceptable range (0.5-1.5)."""
        if not 0.5 <= v <= 1.5:
            raise ValueError(f"TTS speed must be between 0.5 and 1.5. Got: {v}")
        return v

    @field_validator("primary_language")
    @classmethod
    def validate_primary_language(cls, v: str) -> str:
        """Validate primary language is supported."""
        supported_languages = list(LANGUAGE_CONFIG.keys())
        if v not in supported_languages:
            raise ValueError(
                f"Primary language '{v}' is not supported. "
                f"Supported languages: {', '.join(supported_languages)}"
            )
        return v

    @field_validator("target_language")
    @classmethod
    def validate_target_language(cls, v: str) -> str:
        """Validate target language is supported."""
        supported_languages = list(LANGUAGE_CONFIG.keys())
        if v not in supported_languages:
            raise ValueError(
                f"Target language '{v}' is not supported. "
                f"Supported languages: {', '.join(supported_languages)}"
            )
        return v
