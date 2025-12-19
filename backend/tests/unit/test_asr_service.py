import pytest
import sys
from unittest.mock import MagicMock, patch
from app.services.asr_service import ASRService

@pytest.fixture
def asr_service():
    return ASRService()

@pytest.mark.asyncio
async def test_transcribe_mac(asr_service):
    with patch("sys.platform", "darwin"):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = MagicMock(text="Hello world")
        asr_service.model = mock_model
        
        result = await asr_service.transcribe("dummy.wav")
        assert result == "Hello world"
        mock_model.transcribe.assert_called_once_with("dummy.wav")

@pytest.mark.asyncio
async def test_transcribe_win(asr_service):
    with patch("sys.platform", "win32"):
        mock_model = MagicMock()
        # NeMo returns a list of results
        mock_model.transcribe.return_value = [MagicMock(text="Hello world win")]
        asr_service.model = mock_model
        
        result = await asr_service.transcribe("dummy.wav")
        assert result == "Hello world win"
        mock_model.transcribe.assert_called_once_with(["dummy.wav"])

@pytest.mark.asyncio
async def test_transcribe_no_model(asr_service):
    asr_service.model = None
    result = await asr_service.transcribe("dummy.wav")
    assert "mock transcription" in result

from app.core.exceptions import ASRError

@pytest.mark.asyncio
async def test_transcribe_error(asr_service):
    with patch("sys.platform", "darwin"):
        mock_model = MagicMock()
        mock_model.transcribe.side_effect = Exception("ASR Error")
        asr_service.model = mock_model
        
        with pytest.raises(ASRError) as excinfo:
            await asr_service.transcribe("dummy.wav")
        assert "Transcription failed" in str(excinfo.value)
