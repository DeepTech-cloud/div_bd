from fastapi import APIRouter
from app.api.routers import upload, generate, history, settings

api_router = APIRouter()
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
api_router.include_router(generate.router, prefix="/generate", tags=["Generate"])
api_router.include_router(history.router, prefix="", tags=["History & Images"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
