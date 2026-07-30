from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.services.ai_generator import AIGenerator
from app.services.prompt_builder import PromptBuilder
from app.schemas.image import GenerateRequest, GenerateResponse

router = APIRouter()

@router.post("/", response_model=GenerateResponse)
def generate_image_endpoint(
    request: GenerateRequest
):
    # Validate local file exists based on image_id (which is public_id/relative path)
    file_path = Path(settings.UPLOAD_DIR) / request.image_id
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Build daily prompt
        prompt = PromptBuilder.get_today_prompt()

        # Pass local file path so generator can read raw image bytes from disk
        generated_url = AIGenerator.generate_image(prompt, str(file_path))

        return GenerateResponse(generated_url=generated_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
