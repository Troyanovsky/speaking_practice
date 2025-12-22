import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.schemas.history import SessionHistoryDetail, SessionHistoryItem
from app.schemas.session import Feedback, Turn


class HistoryService:
    """Service for persisting and retrieving session history."""

    def __init__(self) -> None:
        self.history_file = os.path.join(settings.DATA_DIR, "session_history.json")
        self._history: Optional[List[Dict[str, Any]]] = None

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history from disk."""
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, "r") as f:
                data: Any = json.load(f)
                return List[Dict[str, Any]](data)
        except Exception as e:
            print(f"Error loading history: {e}")
            return []

    def _save_history(self) -> None:
        """Persist history to disk."""
        if self._history is not None:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
                with open(self.history_file, "w") as f:
                    json.dump(self._history, f, indent=2)
            except Exception as e:
                print(f"Error saving history: {e}")

    def _get_history(self) -> List[Dict[str, Any]]:
        """Get cached history, loading from disk if needed."""
        if self._history is None:
            self._history = self._load_history()
        return self._history

    def save_session(
        self,
        session_id: str,
        settings_data: Dict[str, Any],
        history: List[Dict[str, str]],
        summary: str,
        feedback: List[Dict[str, str]],
    ) -> None:
        """Save a completed session to history."""
        sessions = self._get_history()

        session_record = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "primary_language": settings_data.get("primary_language", "Unknown"),
            "target_language": settings_data.get("target_language", "Unknown"),
            "proficiency_level": settings_data.get("proficiency_level", "Unknown"),
            "turn_count": len([h for h in history if h.get("role") == "user"]),
            "turns": history,
            "summary": summary,
            "feedback": feedback,
        }

        sessions.append(session_record)
        self._history = sessions
        self._save_history()

    def get_all_sessions(self) -> List[SessionHistoryItem]:
        """Get list of all sessions for history list view."""
        sessions = self._get_history()

        # Sort by timestamp, newest first
        sorted_sessions = sorted(
            sessions, key=lambda x: x.get("timestamp", ""), reverse=True
        )

        return [
            SessionHistoryItem(
                session_id=s["session_id"],
                timestamp=s["timestamp"],
                primary_language=s["primary_language"],
                target_language=s["target_language"],
                proficiency_level=s["proficiency_level"],
                turn_count=s["turn_count"],
                summary=(
                    s.get("summary", "")[:100] + "..."
                    if len(s.get("summary", "")) > 100
                    else s.get("summary", "")
                ),
            )
            for s in sorted_sessions
        ]

    def get_session_by_id(self, session_id: str) -> Optional[SessionHistoryDetail]:
        """Get full session detail by ID."""
        sessions = self._get_history()

        for s in sessions:
            if s["session_id"] == session_id:
                return SessionHistoryDetail(
                    session_id=s["session_id"],
                    timestamp=s["timestamp"],
                    primary_language=s["primary_language"],
                    target_language=s["target_language"],
                    proficiency_level=s["proficiency_level"],
                    turn_count=s["turn_count"],
                    turns=[
                        Turn(role=t["role"], text=t["content"])
                        for t in s.get("turns", [])
                    ],
                    summary=s.get("summary", ""),
                    feedback=[Feedback(**f) for f in s.get("feedback", [])],
                )

        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session from history."""
        sessions = self._get_history()
        original_length = len(sessions)

        self._history = [s for s in sessions if s["session_id"] != session_id]

        if len(self._history) < original_length:
            self._save_history()
            return True
        return False


history_service = HistoryService()
