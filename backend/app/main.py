from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.services.asr_service import asr_service
from app.services.tts_service import tts_service
from app.services.session_manager import session_manager
import os
import uvicorn
import asyncio

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    print("Starting up... Loading AI models.")
    asr_service.load_model()
    tts_service.load_model()
    print("AI models loaded.")
    
    # Start session cleanup background task
    asyncio.create_task(session_cleanup_task())

async def session_cleanup_task():
    """Background task to clean up expired sessions every 10 minutes"""
    while True:
        try:
            # Clean up sessions older than 1 hour (3600 seconds)
            removed_count = session_manager.cleanup_expired_sessions(max_age_seconds=3600)
            if removed_count > 0:
                print(f"Cleaned up {removed_count} expired sessions.")
        except Exception as e:
            print(f"Error in session cleanup task: {e}")
        
        # Wait for 10 minutes
        await asyncio.sleep(600)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static directory for audio files
# We mount data/outputs to /static so frontend can access generated audio
# Ensure the directory exists
os.makedirs(settings.AUDIO_OUTPUT_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.AUDIO_OUTPUT_DIR), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to Speaking Practice App API"}

def main():
    """Main entry point for the dev command"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
