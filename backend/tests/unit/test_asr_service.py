import sys
from unittest.mock import MagicMock, patch

import pytest

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
async def test_transcribe_win_tuple(asr_service):
    with patch("sys.platform", "win32"):
        mock_model = MagicMock()
        # NeMo might return a tuple with a Hypothesis-like object
        mock_hypothesis = MagicMock()
        mock_hypothesis.text = "Hello world tuple"
        mock_model.transcribe.return_value = (mock_hypothesis,)
        asr_service.model = mock_model

        result = await asr_service.transcribe("dummy.wav")
        assert result == "Hello world tuple"
        mock_model.transcribe.assert_called_once_with(["dummy.wav"])


@pytest.mark.asyncio
async def test_transcribe_win_dict(asr_service):
    with patch("sys.platform", "win32"):
        mock_model = MagicMock()
        # NeMo might return a list of dictionaries
        mock_model.transcribe.return_value = [{"text": "Hello world dict"}]
        asr_service.model = mock_model

        result = await asr_service.transcribe("dummy.wav")
        assert result == "Hello world dict"
        mock_model.transcribe.assert_called_once_with(["dummy.wav"])


@pytest.mark.asyncio
async def test_transcribe_win_transcription_key(asr_service):
    with patch("sys.platform", "win32"):
        mock_model = MagicMock()
        # NeMo might use 'transcription' key instead of 'text'
        mock_model.transcribe.return_value = [
            {"transcription": "Hello world transcription"}
        ]
        asr_service.model = mock_model

        result = await asr_service.transcribe("dummy.wav")
        assert result == "Hello world transcription"
        mock_model.transcribe.assert_called_once_with(["dummy.wav"])


@pytest.mark.asyncio
async def test_transcribe_win_indexable(asr_service):
    with patch("sys.platform", "win32"):
        mock_model = MagicMock()
        # NeMo might return indexable objects with text as first element
        mock_model.transcribe.return_value = [["Hello world indexable"]]
        asr_service.model = mock_model

        result = await asr_service.transcribe("dummy.wav")
        assert result == "Hello world indexable"
        mock_model.transcribe.assert_called_once_with(["dummy.wav"])


@pytest.mark.asyncio
async def test_transcribe_win_tuple_of_lists(asr_service):
    with patch("sys.platform", "win32"):
        mock_model = MagicMock()
        # Actual NeMo output format: tuple containing lists
        mock_model.transcribe.return_value = (
            ["Hello world tuple list"],
            ["Hello world tuple list"],
        )
        asr_service.model = mock_model

        result = await asr_service.transcribe("dummy.wav")
        assert result == "Hello world tuple list"
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
