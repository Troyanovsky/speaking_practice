"""Session history management endpoints."""

from typing import Dict

from fastapi import APIRouter, HTTPException

from app.schemas.history import HistoryListResponse, SessionHistoryDetail
from app.services.history_service import history_service

router = APIRouter()


@router.get("/", response_model=HistoryListResponse)
async def get_history() -> HistoryListResponse:
    """Get list of all past sessions."""
    sessions = history_service.get_all_sessions()
    return HistoryListResponse(sessions=sessions, total=len(sessions))


@router.get("/{session_id}", response_model=SessionHistoryDetail)
async def get_session_detail(session_id: str) -> SessionHistoryDetail:
    """Get full details of a specific session."""
    session = history_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    """Delete a session from history."""
    deleted = history_service.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


@router.delete("/")
async def delete_all_history() -> Dict[str, str]:
    """Delete all session history."""
    deleted_count = history_service.delete_all_sessions()
    return {"message": f"Deleted {deleted_count} sessions successfully"}
