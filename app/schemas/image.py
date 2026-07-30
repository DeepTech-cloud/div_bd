from pydantic import BaseModel
from typing import Optional

# --- API Response/Request Schemas for Frontend ---

class UploadResponse(BaseModel):
    """Returned after a successful image upload."""
    image_id: str
    image_url: str

class GenerateRequest(BaseModel):
    """Request body for the generate endpoint."""
    image_id: str

class GenerateResponse(BaseModel):
    """Returned after synchronous image generation."""
    generated_url: str
