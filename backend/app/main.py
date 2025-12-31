"""FastAPI application entry point for the Speaking Practice App.

This module initializes the FastAPI application with:
- Exception handlers for custom application exceptions
- CORS middleware configuration
- Startup/shutdown event handlers for model loading and cleanup
- Background session cleanup task
- Static file serving for audio outputs
- API router inclusion
"""

import asyncio
import logging
import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.services.asr_service import asr_service
from app.services.session_manager import session_manager
from app.services.tts_service import tts_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions.

    Args:
        request: The incoming HTTP request.
        exc: The custom application exception.

    Returns:
        JSONResponse with structured error information.
    """
    logger.error(
        f"AppException: {exc.error_code} - {exc.message} - Detail: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: The incoming HTTP request.
        exc: The unexpected exception.

    Returns:
        JSONResponse with generic error information.
    """
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "detail": str(exc),
        },
    )


# Global reference to the cleanup task
cleanup_task = None


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup.

    Loads AI models, cleans up orphaned audio files, and starts
    the background session cleanup task.
    """
    print("Starting up... Loading AI models.")
    asr_service.load_model()
    tts_service.load_model()
    print("AI models loaded.")

    # Clean up orphaned audio files from previous crashes/abnormal termination
    from app.core.audio import cleanup_orphaned_files

    deleted_count = cleanup_orphaned_files(max_age_hours=2)
    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} orphaned audio file(s) from previous runs.")

    # Start session cleanup background task
    global cleanup_task
    cleanup_task = asyncio.create_task(session_cleanup_task())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up resources on shutdown.

    Cancels the background session cleanup task.
    """
    print("Shutting down... cancelling background tasks.")
    global cleanup_task
    if cleanup_task and not cleanup_task.done():
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            print("Cleanup task cancelled successfully.")


async def session_cleanup_task() -> None:
    """Clean up expired sessions periodically.

    Runs in the background, removing sessions older than 1 hour
    every 10 minutes.
    """
    try:
        while True:
            try:
                # Clean up sessions older than 1 hour (3600 seconds)
                removed_count = session_manager.cleanup_expired_sessions(
                    max_age_seconds=3600
                )
                if removed_count > 0:
                    print(f"Cleaned up {removed_count} expired sessions.")
            except Exception as e:
                print(f"Error in session cleanup task: {e}")

            # Wait for 10 minutes
            await asyncio.sleep(600)
    except asyncio.CancelledError:
        print("Session cleanup task received cancellation signal.")
        raise


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
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
def read_root() -> dict[str, str]:
    """Return welcome message.

    Returns:
        Dictionary with welcome message.
    """
    return {"message": "Welcome to Speaking Practice App API"}


def main() -> None:
    """Start the development server."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
