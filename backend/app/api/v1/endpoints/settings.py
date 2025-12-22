"""User settings management endpoints."""

from fastapi import APIRouter

from app.schemas.settings import UserSettings
from app.services.settings_service import settings_service

router = APIRouter()


@router.get("/", response_model=UserSettings)
async def get_settings() -> UserSettings:
    """Get current user settings."""
    return settings_service.get_settings()


@router.post("/", response_model=UserSettings)
async def update_settings(settings: UserSettings) -> UserSettings:
    """Update user settings."""
    return settings_service.update_settings(settings.model_dump())
