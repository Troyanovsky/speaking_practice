"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1.endpoints import history, session, settings

api_router = APIRouter()
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
