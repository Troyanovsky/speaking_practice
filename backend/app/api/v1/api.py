from fastapi import APIRouter
from app.api.v1.endpoints import session, settings

api_router = APIRouter()
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
