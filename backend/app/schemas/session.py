from pydantic import BaseModel
from typing import List, Optional

class Turn(BaseModel):
    role: str  # 'user' or 'system'
    text: str
    audio_url: Optional[str] = None

class SessionCreate(BaseModel):
    primary_language: str
    target_language: str
    proficiency_level: str

class SessionResponse(BaseModel):
    session_id: str
    turns: List[Turn]
    is_active: bool

class TurnResponse(BaseModel):
    user_text: str
    ai_text: str
    ai_audio_url: str
    is_session_ended: bool = False

class Feedback(BaseModel):
    original_sentence: str
    corrected_sentence: str
    explanation: str

class SessionAnalysis(BaseModel):
    summary: str
    feedback: List[Feedback]
