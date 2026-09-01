import logging
from fastapi import APIRouter, HTTPException
from app.storage.firebase_storage import delete_image

logger = logging.getLogger(__name__)
router = APIRouter()

@router.delete("/image/{image_id:path}")
def delete_image_endpoint(image_id: str):
    logger.info(f"Delete request received | image_id={image_id!r}")
    success = delete_image(image_id)
    if not success:
        logger.warning(f"Image not found for deletion | image_id={image_id!r}")
        raise HTTPException(status_code=404, detail="Image not found")
    logger.info(f"Image deleted successfully | image_id={image_id!r}")
    return {"message": "Image deleted successfully"}
