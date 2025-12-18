from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.session import Feedback, Turn


class SessionHistoryItem(BaseModel):
    """Summary item for history list view."""
    session_id: str
    timestamp: str  # ISO format
    primary_language: str
    target_language: str
    proficiency_level: str
    turn_count: int
    summary: str


class SessionHistoryDetail(BaseModel):
    """Full session detail for History detail view."""
    session_id: str
    timestamp: str
    primary_language: str
    target_language: str
    proficiency_level: str
    turn_count: int
    turns: List[Turn]
    summary: str
    feedback: List[Feedback]


class HistoryListResponse(BaseModel):
    """Response for GET /history/."""
    sessions: List[SessionHistoryItem]
    total: int
