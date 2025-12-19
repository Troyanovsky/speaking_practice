import pytest
from app.core.audio import sanitize_filename, validate_audio_extension
from fastapi import HTTPException

def test_sanitize_filename():
    # Basic filename
    assert sanitize_filename("test.wav") == "test.wav"
    
    # Path traversal
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    
    # Special characters
    assert sanitize_filename("test space & special.wav") == "test_space___special.wav"
    
    # None handling
    assert sanitize_filename(None) == "unnamed_audio"
    
    # Length limit
    long_filename = "a" * 300 + ".wav"
    sanitized = sanitize_filename(long_filename)
    assert len(sanitized) <= 255
    assert sanitized.endswith(".wav")

def test_validate_audio_extension():
    # Valid extensions
    validate_audio_extension("test.wav")
    validate_audio_extension("test.MP3")
    validate_audio_extension("audio.m4a")
    
    # Invalid extensions
    with pytest.raises(HTTPException) as excinfo:
        validate_audio_extension("test.txt")
    assert excinfo.value.status_code == 400
    assert "Invalid file extension" in excinfo.value.detail
    
    with pytest.raises(HTTPException) as excinfo:
        validate_audio_extension("script.py")
    assert excinfo.value.status_code == 400
    
    # Double extension
    with pytest.raises(HTTPException) as excinfo:
        validate_audio_extension("malicious.php.wav.txt")
    assert excinfo.value.status_code == 400

    # No extension
    with pytest.raises(HTTPException) as excinfo:
        validate_audio_extension("no_extension")
    assert excinfo.value.status_code == 400
    
    # None handling
    with pytest.raises(HTTPException) as excinfo:
        validate_audio_extension(None)
    assert excinfo.value.status_code == 400
    assert "Missing filename" in excinfo.value.detail
