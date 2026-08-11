from sqlalchemy import Column, String, LargeBinary, DateTime, JSON, func
from app.core.db import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, index=True) # e.g., "uploads/uuid.ext"
    content = Column(LargeBinary, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(JSON, nullable=True)
