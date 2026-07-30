from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.image_processor import ImageProcessor
from app.storage.local_storage import save_image
from app.schemas.image import UploadResponse

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_image_endpoint(
    file: UploadFile = File(...)
):
    try:
        # Read file
        contents = await file.read()
        
        # Process Image (compress, resize, face detection, noise reduction)
        processed_bytes = ImageProcessor.process(contents)
        
        # Detect extension from content-type (default jpg)
        content_type = file.content_type or "image/jpeg"
        ext = content_type.split("/")[-1].replace("jpeg", "jpg")
        
        # Save to local filesystem
        upload_result = save_image(processed_bytes, subfolder="uploads", ext=ext)
        
        # Use relative public_id (path) as the image_id
        return UploadResponse(
            image_id=upload_result["public_id"],
            image_url=upload_result["secure_url"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
