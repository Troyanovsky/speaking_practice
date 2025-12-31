"""Unit tests for LLM service behavior."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import LLMError
from app.services.llm_service import LLMService


@pytest.fixture
def llm_service():
    """Provide an LLM service instance."""
    return LLMService()


@pytest.fixture
def mock_openai():
    """Mock AsyncOpenAI chat completion client."""
    with patch("app.services.llm_service.AsyncOpenAI") as mock:
        client_instance = mock.return_value
        client_instance.chat = MagicMock()
        client_instance.chat.completions = MagicMock()
        client_instance.chat.completions.create = AsyncMock()
        yield client_instance


@pytest.fixture
def mock_settings():
    """Mock settings service response for LLM config."""
    with patch("app.services.llm_service.settings_service") as mock:
        mock_settings_obj = MagicMock()
        mock_settings_obj.llm_api_key = "test-key"
        mock_settings_obj.llm_base_url = "https://test.api"
        mock_settings_obj.llm_model = "test-model"
        mock.get_settings.return_value = mock_settings_obj
        yield mock


@pytest.mark.asyncio
async def test_generate_greeting(llm_service, mock_openai, mock_settings):
    """Generate greeting uses chat completions and returns content."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hola, bienvenido!"
    mock_openai.chat.completions.create.return_value = mock_response

    greeting = await llm_service.generate_greeting("Spanish", "A1")

    assert greeting == "Hola, bienvenido!"
    mock_openai.chat.completions.create.assert_called_once()
    args, kwargs = mock_openai.chat.completions.create.call_args
    assert kwargs["model"] == "test-model"
    assert "Spanish" in kwargs["messages"][0]["content"]


@pytest.mark.asyncio
async def test_get_response(llm_service, mock_openai, mock_settings):
    """Get response returns assistant message content."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "I am doing well."
    mock_openai.chat.completions.create.return_value = mock_response

    history = [{"role": "user", "content": "How are you?"}]
    response = await llm_service.get_response(history, "English", "B1")

    assert response == "I am doing well."
    mock_openai.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_grammar(llm_service, mock_openai, mock_settings):
    """Analyze grammar returns parsed analysis output."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"summary": "Good", "feedback": []}'
    mock_openai.chat.completions.create.return_value = mock_response

    history = [{"role": "user", "content": "I has a cat."}]
    analysis = await llm_service.analyze_grammar(history)

    assert analysis.summary == "Good"
    assert analysis.feedback == []
    mock_openai.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_greeting_error(llm_service, mock_openai, mock_settings):
    """Generate greeting should raise LLMError on failures."""
    # Force error
    mock_openai.chat.completions.create.side_effect = Exception("API Error")

    with pytest.raises(LLMError) as excinfo:
        await llm_service.generate_greeting("Spanish", "A1")
    assert "Greeting generation failed" in str(excinfo.value)


def test_clean_text(llm_service):
    """Clean text strips markdown artifacts from output."""
    dirty_text = "**Hello** *world* [link](url) `code` \n- list item\n1. First"
    expected = "Hello world link list item First"
    assert llm_service._clean_text(dirty_text) == expected
