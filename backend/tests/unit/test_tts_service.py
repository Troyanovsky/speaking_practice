import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.tts_service import TTSService

@pytest.fixture
def tts_service():
    return TTSService()

@pytest.fixture
def mock_pipeline():
    with patch("kokoro.KPipeline") as mock:
        pipeline_instance = mock.return_value
        yield pipeline_instance

@pytest.mark.asyncio
async def test_synthesize_success(tts_service, mock_pipeline):
    # Setup mock generator
    mock_audio = MagicMock()
    mock_generator = [("gs", "ps", mock_audio)]
    tts_service.pipeline_object = MagicMock(return_value=mock_generator)
    
    with patch("soundfile.write") as mock_write:
        result = await tts_service.synthesize("Hello")
        
        assert result.startswith("/static/")
        assert result.endswith(".wav")
        mock_write.assert_called_once()
        # Check that it was called with the correct sample rate (24000)
        args, kwargs = mock_write.call_args
        assert args[2] == 24000

@pytest.mark.asyncio
async def test_synthesize_no_model(tts_service):
    tts_service.pipeline_object = None
    result = await tts_service.synthesize("Hello")
    assert result == "/static/mock_audio.wav"

@pytest.mark.asyncio
async def test_synthesize_error(tts_service):
    tts_service.pipeline_object = MagicMock(side_effect=Exception("TTS Error"))
    result = await tts_service.synthesize("Hello")
    assert result == "/static/error_tts.wav"

@pytest.mark.asyncio
async def test_synthesize_empty_generator(tts_service):
    tts_service.pipeline_object = MagicMock(return_value=[])
    result = await tts_service.synthesize("Hello")
    assert result == "/static/error.wav"
