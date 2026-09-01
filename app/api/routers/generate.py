from fastapi import APIRouter, HTTPException
from app.core.firebase import get_storage_bucket
from app.services.ai_generator import AIGenerator
from app.services.prompt_builder import PromptBuilder
from app.schemas.image import GenerateRequest, GenerateResponse

router = APIRouter()

@router.post("", response_model=GenerateResponse)
@router.post("/", response_model=GenerateResponse)
def generate_image_endpoint(request: GenerateRequest):
    # Download image bytes once — validates existence AND provides data for generation
    bucket = get_storage_bucket()
    blob = bucket.blob(request.image_id)
    if not blob.exists():
        raise HTTPException(status_code=404, detail="Image not found in storage")

    try:
        source_image_bytes = blob.download_as_bytes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download image from storage: {e}")

    try:
        # Use provided prompt or build daily theme prompt
        prompt = request.prompt if (request.prompt and request.prompt.strip()) else PromptBuilder.get_today_prompt()

        # Pass bytes directly — no second Firebase fetch inside the generator
        generated_url = AIGenerator.generate_image(
            prompt=prompt,
            source_image_id=request.image_id,
            source_image_bytes=source_image_bytes,
        )

        return GenerateResponse(generated_url=generated_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
