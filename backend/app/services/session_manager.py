"""Session management service for the Speaking Practice App.

This module provides the SessionManager class which handles:
- Creating and managing conversation sessions
- Processing user audio turns (ASR → LLM → TTS pipeline)
- Session lifecycle management (start, stop, end, cleanup)
- Session history tracking and analysis
- Automatic cleanup of expired sessions
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from app.core.audio import cleanup_session_files
from app.core.exceptions import LLMError, SessionError, SessionNotFoundError, TTSError
from app.schemas.session import (
    SessionAnalysis,
    SessionCreate,
    SessionResponse,
    Turn,
    TurnResponse,
)
from app.services.asr_service import asr_service
from app.services.history_service import history_service
from app.services.llm_service import llm_service
from app.services.tts_service import tts_service


class SessionManager:
    """Manages conversation sessions and orchestrates the AI pipeline.

    Handles session creation, turn processing, and lifecycle management
    with integration to ASR, LLM, and TTS services.
    """

    def __init__(self) -> None:
        """Initialize the session manager."""
        self.sessions: Dict[str, Dict] = {}

    async def create_session(self, settings: SessionCreate) -> SessionResponse:
        """Create a new conversation session.

        Args:
            settings: Session configuration including language settings.

        Returns:
            SessionResponse with session ID and initial greeting turn.

        Raises:
            SessionError: If session creation fails.
            LLMError: If greeting generation fails.
            TTSError: If audio synthesis fails.
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "settings": settings,
            "history": [],
            "turn_count": 0,
            "is_active": True,
            "last_activity": datetime.now(timezone.utc),
        }

        try:
            # Generate LLM greeting based on user settings
            greeting = await llm_service.generate_greeting(
                settings.target_language,
                settings.proficiency_level,
                settings.primary_language,
            )

            # Synthesize audio for the greeting
            greeting_audio_url = await tts_service.synthesize(
                greeting,
                target_language=settings.target_language,
                session_id=session_id,
            )

            self.sessions[session_id]["history"].append(
                {"role": "assistant", "content": greeting}
            )

            return SessionResponse(
                session_id=session_id,
                turns=[
                    Turn(role="assistant", text=greeting, audio_url=greeting_audio_url)
                ],
                is_active=True,
            )
        except Exception as e:
            # If initialization fails, clean up the session entry
            if session_id in self.sessions:
                del self.sessions[session_id]
            if isinstance(e, (LLMError, TTSError)):
                raise e
            raise SessionError(message=f"Failed to start session: {str(e)}")

    def _check_stop_word(self, session: Dict, user_text: str) -> bool:
        """Check if user said the stop word to end the session."""
        stop_word = (
            session["settings"].stop_word.lower()
            if session["settings"].stop_word
            else "stop session"
        )
        return stop_word in user_text.lower()

    async def _handle_stop_word_response(
        self, session: Dict, session_id: str, user_text: str
    ) -> TurnResponse:
        """Handle the response when user says stop word."""
        # Trigger wrap-up
        session["history"].append({"role": "user", "content": user_text})

        # Generate wrap-up message
        wrap_up_prompt = "The user has decided to stop the session. Please provide a brief, polite wrap-up message in the target language."
        session["history"].append({"role": "system", "content": wrap_up_prompt})

        ai_text = await llm_service.get_response(
            session["history"],
            session["settings"].target_language,
            session["settings"].proficiency_level,
        )

        # Synthesize
        ai_audio_url = await tts_service.synthesize(
            ai_text,
            target_language=session["settings"].target_language,
            session_id=session_id,
        )

        session["is_active"] = False
        return TurnResponse(
            user_text=user_text,
            ai_text=ai_text,
            ai_audio_url=ai_audio_url,
            is_session_ended=True,
            is_session_ending=True,
        )

    def _check_max_turns_reached(self, session: Dict) -> bool:
        """Check if max turns (15) has been reached and handle session ending."""
        is_last_turn = session["turn_count"] >= 15

        if is_last_turn:
            session["history"].append(
                {
                    "role": "system",
                    "content": "This is the final turn of the conversation. Please provide a natural closing message to wrap up the session in the target language.",
                }
            )
            session["is_active"] = False

        return is_last_turn

    async def _generate_response(
        self, session: Dict, session_id: str, user_text: str, is_last_turn: bool
    ) -> TurnResponse:
        """Generate AI response and synthesize audio."""
        ai_text = await llm_service.get_response(
            session["history"],
            session["settings"].target_language,
            session["settings"].proficiency_level,
        )
        session["history"].append({"role": "assistant", "content": ai_text})

        # Synthesize Audio
        ai_audio_url = await tts_service.synthesize(
            ai_text,
            target_language=session["settings"].target_language,
            session_id=session_id,
        )

        return TurnResponse(
            user_text=user_text,
            ai_text=ai_text,
            ai_audio_url=ai_audio_url,
            is_session_ended=not session["is_active"],
            is_session_ending=is_last_turn,
        )

    async def process_turn(self, session_id: str, audio_file_path: str) -> TurnResponse:
        """Process a user audio turn in the conversation.

        Args:
            session_id: The session identifier.
            audio_file_path: Path to the uploaded audio file.

        Returns:
            TurnResponse with transcribed user text, AI response, and audio.

        Raises:
            SessionNotFoundError: If session doesn't exist.
            SessionError: If session is inactive.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        if not session["is_active"]:
            raise SessionError(message="Cannot process turn on an inactive session")

        # Update last activity
        session["last_activity"] = datetime.now(timezone.utc)

        # 1. Transcribe
        user_text = await asr_service.transcribe(audio_file_path)

        # 2. Check for stop word
        if self._check_stop_word(session, user_text):
            return await self._handle_stop_word_response(session, session_id, user_text)

        # 3. Update history and turn count
        session["history"].append({"role": "user", "content": user_text})
        session["turn_count"] += 1

        # 4. Check if max turns reached
        is_last_turn = self._check_max_turns_reached(session)

        # 5. Generate response and synthesize
        return await self._generate_response(
            session, session_id, user_text, is_last_turn
        )

    async def end_session(self, session_id: str) -> SessionAnalysis:
        """End a session and generate grammar analysis.

        Args:
            session_id: The session identifier.

        Returns:
            SessionAnalysis with grammar feedback and conversation summary.

        Raises:
            SessionNotFoundError: If session doesn't exist.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        session["is_active"] = False
        analysis = await llm_service.analyze_grammar(
            session["history"],
            session["settings"].primary_language,
            session["settings"].target_language,
        )

        # Save session to history for persistence
        history_service.save_session(
            session_id=session_id,
            settings_data={
                "primary_language": session["settings"].primary_language,
                "target_language": session["settings"].target_language,
                "proficiency_level": session["settings"].proficiency_level,
            },
            history=session["history"],
            summary=analysis.summary,
            feedback=[f.model_dump() for f in analysis.feedback],
        )

        # 2. Perform cleanup of audio files
        cleanup_session_files(session_id)

        return analysis

    async def stop_session(self, session_id: str) -> TurnResponse:
        """Manually stop a session with a wrap-up message.

        Args:
            session_id: The session identifier.

        Returns:
            TurnResponse with wrap-up message and audio.

        Raises:
            SessionNotFoundError: If session doesn't exist.
            SessionError: If session is already inactive.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        if not session["is_active"]:
            raise SessionError(message="Cannot stop an inactive session")

        # Generate wrap-up message
        wrap_up_prompt = "The user has decided to stop the session. Please provide a brief, polite wrap-up message in the target language."
        session["history"].append({"role": "system", "content": wrap_up_prompt})

        ai_text = await llm_service.get_response(
            session["history"],
            session["settings"].target_language,
            session["settings"].proficiency_level,
        )

        # Synthesize
        ai_audio_url = await tts_service.synthesize(
            ai_text,
            target_language=session["settings"].target_language,
            session_id=session_id,
        )

        session["history"].append({"role": "assistant", "content": ai_text})
        session["is_active"] = False

        return TurnResponse(
            user_text="",
            ai_text=ai_text,
            ai_audio_url=ai_audio_url,
            is_session_ended=True,
            is_session_ending=True,
        )

    def get_session_history(self, session_id: str) -> List[Turn]:
        """Get the conversation history for a session.

        Args:
            session_id: The session identifier.

        Returns:
            List of turns in the conversation.
        """
        session = self.sessions.get(session_id)
        if not session:
            return []

        return [Turn(role=h["role"], text=h["content"]) for h in session["history"]]

    def cleanup_expired_sessions(self, max_age_seconds: int = 3600) -> int:
        """Remove expired sessions and clean up their files.

        Args:
            max_age_seconds: Maximum age of sessions before cleanup (default: 3600).

        Returns:
            Number of sessions removed.
        """
        now = datetime.now(timezone.utc)
        expired_ids = []

        for session_id, session in self.sessions.items():
            last_activity = session.get("last_activity")
            if not last_activity:
                # Fallback for sessions created before this change (if any exist in long-running process)
                expired_ids.append(session_id)
                continue

            delta = (now - last_activity).total_seconds()
            if delta > max_age_seconds:
                expired_ids.append(session_id)

        for session_id in expired_ids:
            # Clean up audio files before removing from memory
            cleanup_session_files(session_id)
            del self.sessions[session_id]

        return len(expired_ids)


session_manager = SessionManager()
