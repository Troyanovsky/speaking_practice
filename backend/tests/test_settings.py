import os
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.settings_service import settings_service
from app.schemas.settings import UserSettings

client = TestClient(app)

# Use a test settings file
TEST_SETTINGS_FILE = os.path.join(settings.AUDIO_UPLOAD_DIR, "..", "test_user_settings.json")
TEST_SETTINGS_FILE = os.path.abspath(TEST_SETTINGS_FILE)

@pytest.fixture
def mock_settings_service(monkeypatch):
    """Mock the settings service to use a test file."""
    # Patch the settings file path
    monkeypatch.setattr(settings_service, "settings_file", TEST_SETTINGS_FILE)
    # Reset internal state
    settings_service._settings = None
    
    # Clean up before test
    if os.path.exists(TEST_SETTINGS_FILE):
        os.remove(TEST_SETTINGS_FILE)
        
    yield settings_service
    
    # Clean up after test
    if os.path.exists(TEST_SETTINGS_FILE):
        os.remove(TEST_SETTINGS_FILE)

def test_get_settings_defaults(mock_settings_service):
    """Test that default settings are returned when no file exists."""
    response = client.get("/api/v1/settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["primary_language"] == "English"
    assert data["target_language"] == "Spanish"
    # LLM Defaults from env (or app_settings defaults)
    assert data["llm_base_url"] == settings.LLM_BASE_URL

def test_update_and_persist_settings(mock_settings_service):
    """Test that settings can be updated and are persisted to disk."""
    new_settings = {
        "primary_language": "French",
        "target_language": "Italian",
        "proficiency_level": "C1",
        "stop_word": "halt",
        "llm_base_url": "https://test.api.com",
        "llm_api_key": "test-key",
        "llm_model": "gpt-99"
    }
    
    # Update settings
    response = client.post("/api/v1/settings/", json=new_settings)
    assert response.status_code == 200
    data = response.json()
    assert data["primary_language"] == "French"
    assert data["target_language"] == "Italian"
    
    # Verify persistence
    assert os.path.exists(TEST_SETTINGS_FILE)
    with open(TEST_SETTINGS_FILE, "r") as f:
        saved_data = json.load(f)
        assert saved_data["primary_language"] == "French"
        assert saved_data["llm_api_key"] == "test-key"

def test_get_settings_loads_persisted(mock_settings_service):
    """Test that GET settings loads from disk if file exists."""
    # Create a pre-existing settings file
    pre_existing = {
        "primary_language": "Italian",
        "target_language": "Portuguese",
        "proficiency_level": "B2",
        "stop_word": "basta",
        "llm_base_url": "https://api.openai.com/v1",
        "llm_api_key": "existing-key",
        "llm_model": "gpt-4"
    }
    with open(TEST_SETTINGS_FILE, "w") as f:
        json.dump(pre_existing, f)
        
    # Reset service internal cache to force reload
    mock_settings_service._settings = None
    
    response = client.get("/api/v1/settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["primary_language"] == "Italian"
    assert data["llm_api_key"] == "existing-key"
