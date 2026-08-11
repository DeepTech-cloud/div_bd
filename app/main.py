from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import api_router
from app.core.db import init_db, SessionLocal
from app.core.models import Image

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
def startup_event():
    import logging
    logger = logging.getLogger("uvicorn.error")
    try:
        init_db()
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}. FastAPI starting up anyway to prevent container crash.")


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def health_check():
    return {"status": "health check passed"}

@app.get("/health")
def health_check():
    return {"status": "Api is running"}

app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve stored images from PostgreSQL at /static/<path>
@app.get("/static/{image_id:path}")
def serve_image(image_id: str):
    db = SessionLocal()
    try:
        db_image = db.query(Image).filter(Image.id == image_id).first()
        if not db_image:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=db_image.content, media_type=db_image.content_type)
    finally:
        db.close()

