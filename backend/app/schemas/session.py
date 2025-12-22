"""Pydantic schemas for session management and conversation data.

This module defines schemas for:
- Conversation turns and responses
- Session creation and management
- Grammar feedback and analysis
"""

from typing import List, Optional

from pydantic import BaseModel


class Turn(BaseModel):
    """Represents a single turn in the conversation."""

    role: str  # 'user', 'assistant', or 'system'
    text: str
    audio_url: Optional[str] = None


class SessionCreate(BaseModel):
    """Schema for creating a new practice session."""

    primary_language: str
    target_language: str
    proficiency_level: str
    stop_word: Optional[str] = "stop session"


class SessionResponse(BaseModel):
    """Schema for session creation response with initial turn."""

    session_id: str
    turns: List[Turn]
    is_active: bool


class TurnResponse(BaseModel):
    """Schema for processing a user turn with AI response."""

    user_text: str
    ai_text: str
    ai_audio_url: str
    is_session_ended: bool = False
    is_session_ending: bool = False


class Feedback(BaseModel):
    """Schema for grammar feedback on user sentences."""

    original_sentence: str
    corrected_sentence: str
    explanation: str


class SessionAnalysis(BaseModel):
    """Schema for session grammar analysis results."""

    summary: str
    feedback: List[Feedback]
