from fastapi import APIRouter, HTTPException
from app.storage.firebase_storage import delete_image

router = APIRouter()

@router.delete("/image/{image_id:path}")
def delete_image_endpoint(image_id: str):
    success = delete_image(image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}
