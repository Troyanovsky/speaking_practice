import uuid
from typing import Dict, List, Optional
from app.schemas.session import SessionCreate, Turn, SessionResponse, TurnResponse, SessionAnalysis
from app.services.llm_service import llm_service
from app.services.asr_service import asr_service
from app.services.tts_service import tts_service

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
        
        # Initial greeting
        greeting = "Hello! I am your speaking practice partner. What would you like to talk about today?"
        self.sessions[session_id]["history"].append({"role": "system", "content": greeting})
        
        return SessionResponse(
            session_id=session_id,
            turns=[Turn(role="system", text=greeting)],
            is_active=True
        )

    async def process_turn(self, session_id: str, audio_file_path: str) -> TurnResponse:
        session = self.sessions.get(session_id)
        if not session or not session["is_active"]:
            raise ValueError("Session not found or inactive")

        # 1. Transcribe
        user_text = await asr_service.transcribe(audio_file_path)
        
        # Check for stop word (mock logic)
        if "stop session" in user_text.lower():
            session["is_active"] = False
            return TurnResponse(
                user_text=user_text,
                ai_text="Ending session.",
                ai_audio_url="",
                is_session_ended=True
            )

        # Update history
        session["history"].append({"role": "user", "content": user_text})
        session["turn_count"] += 1

        # 2. Get LLM Response
        ai_text = await llm_service.get_response(session["history"])
        session["history"].append({"role": "system", "content": ai_text})

        # 3. Synthesize Audio
        ai_audio_url = await tts_service.synthesize(ai_text)
        
        # Check max turns
        if session["turn_count"] >= 15:
            session["is_active"] = False
        
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
        return analysis

    def get_session_history(self, session_id: str) -> List[Turn]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return [Turn(role=h["role"], text=h["content"]) for h in session["history"]]

session_manager = SessionManager()
