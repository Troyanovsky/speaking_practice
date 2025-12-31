"""Tests for session-driven settings persistence."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_session_persists_settings():
    """Test session start persists settings as user defaults."""
    # Start a session with custom settings
    session_data = {
        "primary_language": "French",
        "target_language": "Italian",
        "proficiency_level": "C1",
        "stop_word": "arrêter",
    }

    response = client.post("/api/v1/session/start", json=session_data)
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    # Verify settings were persisted
    response = client.get("/api/v1/settings/")
    assert response.status_code == 200
    settings = response.json()

    assert settings["primary_language"] == "French"
    assert settings["target_language"] == "Italian"
    assert settings["proficiency_level"] == "C1"
    assert settings["stop_word"] == "arrêter"

    # Clean up session
    client.post(f"/api/v1/session/{session_id}/end")
