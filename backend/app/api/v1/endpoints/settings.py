from fastapi import APIRouter, HTTPException

from app.schemas.settings import UserSettings
from app.services.settings_service import settings_service

router = APIRouter()


@router.get("/", response_model=UserSettings)
async def get_settings():
    return settings_service.get_settings()


@router.post("/", response_model=UserSettings)
async def update_settings(settings: UserSettings):
    return settings_service.update_settings(settings)
