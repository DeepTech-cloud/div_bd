from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.api.routers import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve locally stored images at /static/<path>
_media_dir = Path(settings.UPLOAD_DIR)
_media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_media_dir)), name="static")
