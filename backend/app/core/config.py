import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Speaking Practice App"
    API_V1_STR: str = "/api/v1"
    
    # Audio Settings
    AUDIO_UPLOAD_DIR: str = os.path.join(os.getcwd(), "backend/app/data/uploads")
    AUDIO_OUTPUT_DIR: str = os.path.join(os.getcwd(), "backend/app/data/outputs")
    
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Model Config
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.AUDIO_UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_OUTPUT_DIR, exist_ok=True)
