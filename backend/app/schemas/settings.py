from pydantic import BaseModel
from typing import Optional

class UserSettings(BaseModel):
    primary_language: str = "English"
    target_language: str = "Spanish"
    proficiency_level: str = "A1"
    stop_word: str = "stop session"
    
    # LLM Settings
    llm_base_url: Optional[str] = "https://api.openai.com/v1"
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = "gpt-4o"
