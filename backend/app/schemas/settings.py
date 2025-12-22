from typing import Optional

from pydantic import BaseModel, field_validator

from app.services.tts_service import LANGUAGE_CONFIG


class UserSettings(BaseModel):
    primary_language: str = "English"
    target_language: str = "Spanish"
    proficiency_level: str = "A1"
    stop_word: str = "stop session"

    # LLM Settings
    llm_base_url: Optional[str] = "https://api.openai.com/v1"
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = "gpt-4o"

    @field_validator("primary_language")
    @classmethod
    def validate_primary_language(cls, v):
        supported_languages = list(LANGUAGE_CONFIG.keys())
        if v not in supported_languages:
            raise ValueError(
                f"Primary language '{v}' is not supported. Supported languages: {', '.join(supported_languages)}"
            )
        return v

    @field_validator("target_language")
    @classmethod
    def validate_target_language(cls, v):
        supported_languages = list(LANGUAGE_CONFIG.keys())
        if v not in supported_languages:
            raise ValueError(
                f"Target language '{v}' is not supported. Supported languages: {', '.join(supported_languages)}"
            )
        return v
