from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import api_router
from app.core.firebase import init_firebase

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
def startup_event():
    import logging
    logger = logging.getLogger("uvicorn.error")
    try:
        init_firebase()
    except Exception as e:
        logger.critical(f"Firebase initialization failed: {e}. FastAPI starting up anyway to prevent container crash.")


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

app.include_router(api_router, prefix=settings.API_V1_STR)



