import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.tts_service import TTSService, LANGUAGE_CONFIG

@pytest.fixture
def tts_service():
    return TTSService()

@pytest.fixture
def mock_pipeline_class():
    with patch("kokoro.KPipeline") as mock:
        yield mock

@pytest.mark.asyncio
async def test_synthesize_success(tts_service, mock_pipeline_class):
    # Setup mock pipeline instance and generator
    mock_pipeline_instance = mock_pipeline_class.return_value
    mock_audio = MagicMock()
    mock_generator = [("gs", "ps", mock_audio)]
    mock_pipeline_instance.return_value = mock_generator
    
    with patch("soundfile.write") as mock_write:
        # Test Default (English)
        result = await tts_service.synthesize("Hello")
        assert result.startswith("/static/")
        mock_pipeline_class.assert_called_with(lang_code='a', repo_id='hexgrad/Kokoro-82M')
        mock_pipeline_instance.assert_called_with("Hello", voice='af_heart', speed=1, split_pattern=r'\n+')

        # Test Spanish with session_id
        mock_pipeline_class.reset_mock()
        session_id = "test-session"
        result = await tts_service.synthesize("Hola", target_language="Spanish", session_id=session_id)
        assert result.startswith(f"/static/{session_id}_")
        mock_pipeline_class.assert_called_with(lang_code='e', repo_id='hexgrad/Kokoro-82M')
        mock_pipeline_instance.assert_called_with("Hola", voice='ef_dora', speed=1, split_pattern=r'\n+')

@pytest.mark.asyncio
async def test_single_pipeline_caching(tts_service, mock_pipeline_class):
    mock_pipeline_instance = mock_pipeline_class.return_value
    mock_pipeline_instance.return_value = [("gs", "ps", MagicMock())]
    
    with patch("soundfile.write"):
        # 1. Load English
        await tts_service.synthesize("Hello", target_language="English")
        assert tts_service.current_lang_code == 'a'
        assert mock_pipeline_class.call_count == 1
        
        # 2. Load English again (should NOT re-initialize)
        await tts_service.synthesize("Hello again", target_language="English")
        assert mock_pipeline_class.call_count == 1
        
        # 3. Load Spanish (should re-initialize)
        await tts_service.synthesize("Hola", target_language="Spanish")
        assert tts_service.current_lang_code == 'e'
        assert mock_pipeline_class.call_count == 2

@pytest.mark.asyncio
async def test_synthesize_no_model(tts_service):
    # If kokoro is not installed, it falls back to mock
    with patch("kokoro.KPipeline", side_effect=ImportError):
        result = await tts_service.synthesize("Hello")
        assert result == "/static/mock_audio.wav"

@pytest.mark.asyncio
async def test_synthesize_error(tts_service, mock_pipeline_class):
    mock_pipeline_instance = mock_pipeline_class.return_value
    mock_pipeline_instance.side_effect = Exception("TTS Error")
    
    result = await tts_service.synthesize("Hello")
    assert result == "/static/error_tts.wav"
