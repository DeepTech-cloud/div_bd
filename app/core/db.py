import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import models here to register them with Base
    from app.core import models
    
    # Retry up to 5 times with exponential/linear backoff
    for attempt in range(5):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables initialized successfully.")
            return
        except Exception as e:
            logger.warning(f"Database initialization attempt {attempt + 1} failed: {e}")
            if attempt < 4:
                time.sleep(2)
            else:
                raise e

