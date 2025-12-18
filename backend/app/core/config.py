import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Speaking Practice App"
    API_V1_STR: str = "/api/v1"
    
    # Audio Settings
    AUDIO_UPLOAD_DIR: str = os.path.join(os.getcwd(), "backend/app/data/uploads")
    AUDIO_OUTPUT_DIR: str = os.path.join(os.getcwd(), "backend/app/data/outputs")
    
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
