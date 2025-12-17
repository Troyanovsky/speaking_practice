from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
import os

app = FastAPI(title=settings.PROJECT_NAME)

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
