from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_session_manager():
    with patch("app.api.v1.endpoints.session.session_manager") as mock:
        yield mock


@pytest.fixture
def mock_history_service():
    with patch("app.api.v1.endpoints.history.history_service") as mock:
        yield mock


def test_start_session(mock_session_manager):
    # Setup mock
    mock_response = MagicMock()
    mock_response.session_id = "test-id"
    mock_response.is_active = True
    mock_response.turns = []
    mock_session_manager.create_session = AsyncMock(return_value=mock_response)

    response = client.post(
        "/api/v1/session/start",
        json={
            "primary_language": "English",
            "target_language": "Spanish",
            "proficiency_level": "A1",
        },
    )

    assert response.status_code == 200
    assert response.json()["session_id"] == "test-id"
    mock_session_manager.create_session.assert_called_once()


from app.core.exceptions import SessionNotFoundError


def test_process_turn_not_found(mock_session_manager):
    mock_session_manager.process_turn = AsyncMock(
        side_effect=SessionNotFoundError("test-id")
    )

    # Mock save_upload_file
    with patch(
        "app.api.v1.endpoints.session.save_upload_file", return_value="/tmp/test.wav"
    ):
        response = client.post(
            "/api/v1/session/test-id/turn",
            files={"audio": ("test.wav", b"dummy content", "audio/wav")},
        )

        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "SESSION_NOT_FOUND"
        assert "test-id" in data["message"]


def test_get_history(mock_history_service):
    mock_history_service.get_all_sessions.return_value = [
        {
            "session_id": "1",
            "timestamp": "2024-01-01T00:00:00",
            "primary_language": "English",
            "target_language": "Spanish",
            "proficiency_level": "A1",
            "turn_count": 5,
            "summary": "Short",
        }
    ]

    response = client.get("/api/v1/history/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["session_id"] == "1"


def test_get_history_detail(mock_history_service):
    mock_detail = MagicMock()
    mock_detail.session_id = "1"
    mock_detail.timestamp = "2024-01-01T00:00:00"
    mock_detail.primary_language = "English"
    mock_detail.target_language = "Spanish"
    mock_detail.proficiency_level = "A1"
    mock_detail.turn_count = 5
    mock_detail.turns = []
    mock_detail.summary = "Summary"
    mock_detail.feedback = []
    mock_history_service.get_session_by_id.return_value = mock_detail

    response = client.get("/api/v1/history/1")

    assert response.status_code == 200
    assert response.json()["session_id"] == "1"


def test_delete_history(mock_history_service):
    mock_history_service.delete_session.return_value = True

    response = client.delete("/api/v1/history/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Session deleted successfully"
