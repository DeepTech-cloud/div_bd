import logging
from fastapi import APIRouter, HTTPException
from app.core.firebase import get_storage_bucket
from app.services.ai_generator import AIGenerator
from app.services.prompt_builder import PromptBuilder
from app.schemas.image import GenerateRequest, GenerateResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=GenerateResponse)
@router.post("/", response_model=GenerateResponse)
def generate_image_endpoint(request: GenerateRequest):
    logger.info(f"Generate request received | image_id={request.image_id!r} | custom_prompt={'yes' if request.prompt and request.prompt.strip() else 'no'}")

    # Download image bytes once — validates existence AND provides data for generation
    bucket = get_storage_bucket()
    blob = bucket.blob(request.image_id)
    if not blob.exists():
        logger.warning(f"Image not found in storage | image_id={request.image_id!r}")
        raise HTTPException(status_code=404, detail="Image not found in storage")

    try:
        source_image_bytes = blob.download_as_bytes()
        logger.info(f"Source image downloaded | image_id={request.image_id!r} | size={len(source_image_bytes)} bytes")
    except Exception as e:
        logger.error(f"Failed to download image from storage | image_id={request.image_id!r} | error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to download image from storage: {e}")

    try:
        # Use provided prompt or build daily theme prompt
        if request.prompt and request.prompt.strip():
            prompt = request.prompt
            logger.info("Using custom prompt provided in request")
        else:
            prompt = PromptBuilder.get_today_prompt()
            logger.info("Using auto-generated daily theme prompt")

        logger.info("Calling Gemini for image generation...")
        # Pass bytes directly — no second Firebase fetch inside the generator
        generated_url = AIGenerator.generate_image(
            prompt=prompt,
            source_image_id=request.image_id,
            source_image_bytes=source_image_bytes,
        )

        logger.info(f"Image generation successful | generated_url={generated_url}")
        return GenerateResponse(generated_url=generated_url)
    except Exception as e:
        logger.error(f"Image generation failed | image_id={request.image_id!r} | error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
