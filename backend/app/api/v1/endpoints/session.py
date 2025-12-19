from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from app.schemas.session import SessionCreate, SessionResponse, TurnResponse, SessionAnalysis
from app.services.session_manager import session_manager
from app.services.settings_service import settings_service
from app.core.config import settings
from app.core.audio import save_upload_file, sanitize_filename, validate_audio_extension
import os

router = APIRouter()

@router.post("/start", response_model=SessionResponse)
async def start_session(session_create: SessionCreate):
    # Persist session settings as user defaults
    settings_service.update_settings({
        "primary_language": session_create.primary_language,
        "target_language": session_create.target_language,
        "proficiency_level": session_create.proficiency_level,
        "stop_word": session_create.stop_word
    })
    
    return await session_manager.create_session(session_create)

@router.post("/{session_id}/turn", response_model=TurnResponse)
async def process_turn(session_id: str, audio: UploadFile = File(...)):
    # Validate and sanitize
    validate_audio_extension(audio.filename)
    safe_filename = sanitize_filename(audio.filename)
    
    # Save audio file
    file_path = os.path.join(settings.AUDIO_UPLOAD_DIR, f"{session_id}_{safe_filename}")
    saved_path = save_upload_file(audio.file, file_path)
    
    # Process
    return await session_manager.process_turn(session_id, saved_path)

@router.post("/{session_id}/end", response_model=SessionAnalysis)
async def end_session(session_id: str):
    return await session_manager.end_session(session_id)
