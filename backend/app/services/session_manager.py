import uuid
from typing import Dict, List, Optional
from app.schemas.session import SessionCreate, Turn, SessionResponse, TurnResponse, SessionAnalysis
from app.services.llm_service import llm_service
from app.services.asr_service import asr_service
from app.services.tts_service import tts_service
from app.services.history_service import history_service

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    async def create_session(self, settings: SessionCreate) -> SessionResponse:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "settings": settings,
            "history": [],
            "turn_count": 0,
            "is_active": True
        }
        
        # Generate LLM greeting based on user settings
        greeting = await llm_service.generate_greeting(
            settings.target_language,
            settings.proficiency_level
        )
        
        # Synthesize audio for the greeting
        greeting_audio_url = await tts_service.synthesize(
            greeting, 
            target_language=settings.target_language
        )
        
        self.sessions[session_id]["history"].append({"role": "assistant", "content": greeting})
        
        return SessionResponse(
            session_id=session_id,
            turns=[Turn(role="system", text=greeting, audio_url=greeting_audio_url)],
            is_active=True
        )

    async def process_turn(self, session_id: str, audio_file_path: str) -> TurnResponse:
        session = self.sessions.get(session_id)
        if not session or not session["is_active"]:
            raise ValueError("Session not found or inactive")

        # 1. Transcribe
        user_text = await asr_service.transcribe(audio_file_path)
        
        # Check for stop word
        stop_word = session["settings"].stop_word.lower() if session["settings"].stop_word else "stop session"
        if stop_word in user_text.lower():
            # Trigger wrap-up
            session["history"].append({"role": "user", "content": user_text})
            
            # Generate wrap-up message
            wrap_up_prompt = "The user has decided to stop the session. Please provide a brief, polite wrap-up message in the target language."
            # Append a system instruction temporarily or just append to history as a system note? 
            # Actually, we can just append a system message to history for the LLM to see, 
            # or better, just pass it as a user message context override?
            # Let's append a specific system instruction to the history for this turn
            session["history"].append({"role": "system", "content": wrap_up_prompt})
            
            ai_text = await llm_service.get_response(
                session["history"],
                session["settings"].target_language,
                session["settings"].proficiency_level
            )
            
            # Synthesize
            ai_audio_url = await tts_service.synthesize(
                ai_text,
                target_language=session["settings"].target_language
            )
            
            session["is_active"] = False
            return TurnResponse(
                user_text=user_text,
                ai_text=ai_text,
                ai_audio_url=ai_audio_url,
                is_session_ended=True
            )

        # Update history
        session["history"].append({"role": "user", "content": user_text})
        session["turn_count"] += 1

        # 2. Get LLM Response with user settings
        # Check if max turns reached to inject wrap-up prompt
        is_last_turn = session["turn_count"] >= 15
        
        if is_last_turn:
            session["history"].append({"role": "system", "content": "This is the final turn of the conversation. Please provide a natural closing message to wrap up the session in the target language."})
            session["is_active"] = False

        ai_text = await llm_service.get_response(
            session["history"],
            session["settings"].target_language,
            session["settings"].proficiency_level
        )
        session["history"].append({"role": "assistant", "content": ai_text})

        # 3. Synthesize Audio
        ai_audio_url = await tts_service.synthesize(
            ai_text,
            target_language=session["settings"].target_language
        )
        
        return TurnResponse(
            user_text=user_text,
            ai_text=ai_text,
            ai_audio_url=ai_audio_url,
            is_session_ended=not session["is_active"]
        )

    async def end_session(self, session_id: str) -> SessionAnalysis:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        
        session["is_active"] = False
        analysis = await llm_service.analyze_grammar(session["history"])
        
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
            feedback=[f.model_dump() for f in analysis.feedback]
        )
        
        return analysis

    def get_session_history(self, session_id: str) -> List[Turn]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return [Turn(role=h["role"], text=h["content"]) for h in session["history"]]

session_manager = SessionManager()
