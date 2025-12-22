import pytest
from pydantic import ValidationError

from app.schemas.settings import UserSettings


def test_valid_language_settings():
    """Test that valid TTS languages are accepted"""
    settings = UserSettings(primary_language="English", target_language="Spanish")
    assert settings.primary_language == "English"
    assert settings.target_language == "Spanish"


def test_invalid_primary_language():
    """Test that invalid primary language is rejected"""
    with pytest.raises(ValidationError) as exc_info:
        UserSettings(primary_language="German")
    assert "Primary language 'German' is not supported" in str(exc_info.value)


def test_invalid_target_language():
    """Test that invalid target language is rejected"""
    with pytest.raises(ValidationError) as exc_info:
        UserSettings(target_language="German")
    assert "Target language 'German' is not supported" in str(exc_info.value)


def test_all_supported_languages():
    """Test that all supported TTS languages are valid"""
    supported_languages = ["English", "Spanish", "French", "Italian", "Portuguese"]

    for lang in supported_languages:
        # Test as primary language
        settings = UserSettings(primary_language=lang)
        assert settings.primary_language == lang

        # Test as target language
        settings = UserSettings(target_language=lang)
        assert settings.target_language == lang


def test_mixed_valid_languages():
    """Test combinations of different valid languages"""
    combinations = [
        ("English", "Spanish"),
        ("French", "Italian"),
        ("Portuguese", "English"),
        ("Spanish", "French"),
    ]

    for primary, target in combinations:
        settings = UserSettings(primary_language=primary, target_language=target)
        assert settings.primary_language == primary
        assert settings.target_language == target
