"""Tests for history service functionality."""

import os

import pytest

from app.services.history_service import HistoryService


@pytest.fixture
def history_service(tmp_path):
    """Create a history service instance with temporary file."""
    service = HistoryService()
    test_file = tmp_path / "test_history.json"
    service.history_file = str(test_file)
    service._history = None
    return service


def test_save_session(history_service):
    """Test saving a session to history."""
    session_id = "test-session-1"
    settings_data = {
        "primary_language": "English",
        "target_language": "Spanish",
        "proficiency_level": "A1",
    }
    history = [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "Hola!"},
    ]
    summary = "A short conversation."
    feedback = [
        {
            "original_sentence": "Hola",
            "corrected_sentence": "Hola",
            "explanation": "None",
        }
    ]

    history_service.save_session(session_id, settings_data, history, summary, feedback)

    assert os.path.exists(history_service.history_file)
    sessions = history_service.get_all_sessions()
    assert len(sessions) == 1
    assert sessions[0].session_id == session_id
    assert sessions[0].target_language == "Spanish"


def test_get_session_by_id(history_service):
    """Test retrieving a session by ID."""
    session_id = "test-session-1"
    settings_data = {
        "primary_language": "English",
        "target_language": "Spanish",
        "proficiency_level": "A1",
    }
    history = [{"role": "user", "content": "Hola"}]

    history_service.save_session(session_id, settings_data, history, "Summary", [])

    detail = history_service.get_session_by_id(session_id)
    assert detail is not None
    assert detail.session_id == session_id
    assert len(detail.turns) == 1
    assert detail.turns[0].text == "Hola"


def test_delete_session(history_service):
    """Test deleting a session from history."""
    session_id = "test-session-1"
    history_service.save_session(session_id, {}, [], "Summary", [])

    assert len(history_service.get_all_sessions()) == 1

    success = history_service.delete_session(session_id)
    assert success is True
    assert len(history_service.get_all_sessions()) == 0


def test_get_all_sessions_sorting(history_service):
    """Test that sessions are sorted by timestamp (newest first)."""
    history_service.save_session("old", {}, [], "Old", [])
    # Small delay needed for timestamp, but consecutive calls should work
    # Let's just mock datetime.now if we need precise order
    history_service.save_session("new", {}, [], "New", [])

    sessions = history_service.get_all_sessions()
    assert len(sessions) == 2
    assert sessions[0].session_id == "new"
    assert sessions[1].session_id == "old"


def test_delete_all_sessions(history_service):
    """Test deleting all sessions from history."""
    history_service.save_session("session1", {}, [], "Summary1", [])
    history_service.save_session("session2", {}, [], "Summary2", [])
    history_service.save_session("session3", {}, [], "Summary3", [])

    assert len(history_service.get_all_sessions()) == 3

    deleted_count = history_service.delete_all_sessions()
    assert deleted_count == 3
    assert len(history_service.get_all_sessions()) == 0

    # Test deleting when empty
    deleted_count_empty = history_service.delete_all_sessions()
    assert deleted_count_empty == 0
