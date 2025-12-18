import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.session_manager import SessionManager
from app.schemas.session import SessionCreate

# Mock data
MOCK_SESSION_ID = "test-session-id"
MOCK_AUDIO_PATH = "/tmp/test.wav"
MOCK_USER_TEXT = "Hello"
MOCK_AI_TEXT = "Hola"
MOCK_AUDIO_URL = "http://localhost:8000/static/audio.wav"

@pytest.fixture
def mock_llm_service():
    with patch("app.services.session_manager.llm_service") as mock:
        mock.generate_greeting = AsyncMock(return_value="Hola, amigo")
        mock.get_response = AsyncMock(return_value=MOCK_AI_TEXT)
        mock.analyze_grammar = AsyncMock(return_value=MagicMock(summary="Good", feedback=[]))
        yield mock

@pytest.fixture
def mock_asr_service():
    with patch("app.services.session_manager.asr_service") as mock:
        mock.transcribe = AsyncMock(return_value=MOCK_USER_TEXT)
        yield mock

@pytest.fixture
def mock_tts_service():
    with patch("app.services.session_manager.tts_service") as mock:
        mock.synthesize = AsyncMock(return_value=MOCK_AUDIO_URL)
        yield mock

@pytest.fixture
def mock_history_service():
    with patch("app.services.session_manager.history_service") as mock:
        mock.save_session = MagicMock()
        yield mock

@pytest.fixture
def session_manager(mock_llm_service, mock_asr_service, mock_tts_service, mock_history_service):
    return SessionManager()

@pytest.mark.asyncio
async def test_create_session(session_manager, mock_llm_service, mock_tts_service):
    settings = SessionCreate(
        primary_language="English", 
        target_language="Spanish", 
        proficiency_level="A1",
        stop_word="stop"
    )
    
    response = await session_manager.create_session(settings)
    
    assert response.session_id is not None
    assert response.is_active is True
    assert len(response.turns) == 1
    assert response.turns[0].text == "Hola, amigo"
    
    # Verify service calls
    mock_llm_service.generate_greeting.assert_called_once_with("Spanish", "A1")
    mock_tts_service.synthesize.assert_called_once_with(
        "Hola, amigo", 
        target_language="Spanish"
    )

@pytest.mark.asyncio
async def test_process_turn_normal(session_manager, mock_asr_service, mock_llm_service, mock_tts_service):
    # Setup active session
    settings = SessionCreate(
        primary_language="English", 
        target_language="Spanish", 
        proficiency_level="A1",
        stop_word="stop"
    )
    session_response = await session_manager.create_session(settings)
    session_id = session_response.session_id
    
    # Process turn
    response = await session_manager.process_turn(session_id, MOCK_AUDIO_PATH)
    
    assert response.user_text == MOCK_USER_TEXT
    assert response.ai_text == MOCK_AI_TEXT
    assert response.is_session_ended is False
    
    # Verify calls
    mock_asr_service.transcribe.assert_called_once_with(MOCK_AUDIO_PATH)
    mock_llm_service.get_response.assert_called_once()
    mock_tts_service.synthesize.assert_called_with(
        MOCK_AI_TEXT, 
        target_language="Spanish"
    )

@pytest.mark.asyncio
async def test_process_turn_stop_word(session_manager, mock_asr_service, mock_llm_service):
    # Setup session
    settings = SessionCreate(
        primary_language="English", 
        target_language="Spanish", 
        proficiency_level="A1",
        stop_word="stop"
    )
    session_response = await session_manager.create_session(settings)
    session_id = session_response.session_id
    
    # Mock ASR to return stop word
    mock_asr_service.transcribe.return_value = "I want to stop now"
    
    response = await session_manager.process_turn(session_id, MOCK_AUDIO_PATH)
    
    assert response.is_session_ended is True
    # Verify wrap-up prompt injection
    # The last message in history before LLM call should be system instruction
    calls = mock_llm_service.get_response.call_args_list
    assert len(calls) > 0
    history_arg = calls[0][0][0] # first call, first arg
    assert history_arg[-1]["role"] == "system"
    assert "wrap-up" in history_arg[-1]["content"]

@pytest.mark.asyncio
async def test_end_session(session_manager, mock_history_service, mock_llm_service):
    # Setup session
    settings = SessionCreate(
        primary_language="English", 
        target_language="Spanish", 
        proficiency_level="A1"
    )
    session_response = await session_manager.create_session(settings)
    session_id = session_response.session_id
    
    analysis = await session_manager.end_session(session_id)
    
    assert analysis is not None
    mock_llm_service.analyze_grammar.assert_called_once()
    mock_history_service.save_session.assert_called_once()
    
    # Verify session is inactive
    assert session_manager.sessions[session_id]["is_active"] is False

@pytest.mark.asyncio
async def test_process_turn_max_turns(session_manager, mock_asr_service, mock_llm_service):
    # Setup session
    settings = SessionCreate(
        primary_language="English", 
        target_language="Spanish", 
        proficiency_level="A1"
    )
    session_response = await session_manager.create_session(settings)
    session_id = session_response.session_id
    
    # Artificially set turn count to 14
    session_manager.sessions[session_id]["turn_count"] = 14
    
    # 15th turn
    response = await session_manager.process_turn(session_id, MOCK_AUDIO_PATH)
    assert response.is_session_ended is True
    # Verify closing prompt injection
    calls = mock_llm_service.get_response.call_args_list
    assert len(calls) > 0
    last_call_history = calls[-1][0][0]
    # Check if the system message for wrap-up was at least present in the history passed
    system_messages = [msg for msg in last_call_history if msg["role"] == "system"]
    assert any("final turn" in msg["content"] for msg in system_messages)
