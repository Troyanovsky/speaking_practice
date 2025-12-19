from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from app.schemas.session import SessionCreate, SessionResponse, TurnResponse, SessionAnalysis
from app.services.session_manager import session_manager
from app.core.config import settings
from app.core.audio import save_upload_file, sanitize_filename, validate_audio_extension
import os

router = APIRouter()

@router.post("/start", response_model=SessionResponse)
async def start_session(session_create: SessionCreate):
    return await session_manager.create_session(session_create)

@router.post("/{session_id}/turn", response_model=TurnResponse)
async def process_turn(session_id: str, audio: UploadFile = File(...)):
    # Validate and sanitize
    validate_audio_extension(audio.filename)
    safe_filename = sanitize_filename(audio.filename)
    safe_session_id = sanitize_filename(session_id)
    
    # Save audio file
    file_path = os.path.join(settings.AUDIO_UPLOAD_DIR, f"{safe_session_id}_{safe_filename}")
    try:
        saved_path = save_upload_file(audio.file, file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not save audio file")
    
    # Process
    try:
        response = await session_manager.process_turn(session_id, saved_path)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/end", response_model=SessionAnalysis)
async def end_session(session_id: str):
    try:
        return await session_manager.end_session(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
