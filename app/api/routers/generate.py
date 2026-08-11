from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.models import Image
from app.services.ai_generator import AIGenerator
from app.services.prompt_builder import PromptBuilder
from app.schemas.image import GenerateRequest, GenerateResponse

router = APIRouter()

@router.post("/", response_model=GenerateResponse)
def generate_image_endpoint(
    request: GenerateRequest,
    db: Session = Depends(get_db)
):
    # Validate image exists in DB based on image_id
    db_image = db.query(Image).filter(Image.id == request.image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Build daily prompt
        prompt = PromptBuilder.get_today_prompt()

        # Pass image_id so generator can read raw image bytes from DB
        generated_url = AIGenerator.generate_image(prompt, request.image_id)

        return GenerateResponse(generated_url=generated_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

