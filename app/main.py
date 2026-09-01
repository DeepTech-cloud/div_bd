import logging
import logging.config
import httpx
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import api_router
from app.core.firebase import init_firebase

# ---------------------------------------------------------------------------
# Logging configuration — applied once at import time so all modules inherit
# ---------------------------------------------------------------------------
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    # Keep uvicorn's own loggers at INFO so they don't duplicate
    "loggers": {
        "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
def startup_event():
    logger.info("=" * 60)
    logger.info(f"Starting up {settings.PROJECT_NAME}")
    logger.info(f"API prefix : {settings.API_V1_STR}")
    logger.info(f"Gemini model: {settings.GEMINI_MODEL}")
    try:
        init_firebase()
        logger.info("Firebase ready")
    except Exception as e:
        logger.critical(f"Firebase initialization failed: {e}. Starting anyway to prevent container crash.")
    logger.info("=" * 60)


@app.on_event("shutdown")
def shutdown_event():
    logger.info(f"{settings.PROJECT_NAME} shutting down")


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
    return {"status": "Api is running"}

@app.get("/proxy-image")
async def proxy_image(url: str):
    """Proxies an external image URL to bypass strict browser CORS policies during local web development."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/jpeg"))
    except Exception as e:
        logger.error(f"Failed to proxy image: {e}")
        raise HTTPException(status_code=500, detail="Failed to proxy image")

app.include_router(api_router, prefix=settings.API_V1_STR)



