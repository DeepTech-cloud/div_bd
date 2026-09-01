import uuid
import datetime
import logging
from app.core.firebase import get_storage_bucket

logger = logging.getLogger(__name__)

def save_image(file_bytes: bytes, subfolder: str = "uploads", ext: str = "jpg") -> dict:
    """
    Saves raw image bytes to Firebase Storage.
    Returns a dict compatible with the expected response shape.
    """
    filename = f"{uuid.uuid4().hex}.{ext}"
    rel_path = f"{subfolder}/{filename}"
    
    logger.info(f"Saving image to Firebase Storage | path={rel_path} | size={len(file_bytes)} bytes")
    
    # Map extension to content-type
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }
    content_type = mime_map.get(ext.lower().replace(".", ""), "image/jpeg")

    bucket = get_storage_bucket()
    blob = bucket.blob(rel_path)
    
    # Upload from string (bytes)
    logger.debug(f"Starting upload for {rel_path}...")
    blob.upload_from_string(file_bytes, content_type=content_type)
    logger.debug(f"Upload complete for {rel_path}")
    
    # Try to make the blob publicly accessible.
    # This fails on buckets with Uniform bucket-level access — fall back to a signed URL.
    try:
        blob.make_public()
        public_url = blob.public_url
        logger.debug(f"Made blob public | path={rel_path}")
    except Exception:
        logger.debug(f"Could not make blob public, generating signed URL | path={rel_path}")
        import datetime
        public_url = blob.generate_signed_url(
            expiration=datetime.timedelta(days=7),
            method="GET",
            version="v4",
        )

    logger.info(f"Image successfully saved | path={rel_path} | url={public_url}")
    return {
        "secure_url": public_url,
        "public_id": rel_path,   # used as the deletion key
        "width": None,
        "height": None,
        "format": ext,
    }

def delete_image(public_id: str) -> bool:
    """
    Deletes an image from Firebase Storage by its public_id.
    Returns True on success, False if the image was not found or error occurred.
    """
    logger.info(f"Attempting to delete image from storage | public_id={public_id!r}")
    try:
        bucket = get_storage_bucket()
        blob = bucket.blob(public_id)
        if blob.exists():
            blob.delete()
            logger.info(f"Image deleted from storage successfully | public_id={public_id!r}")
            return True
        logger.warning(f"Image not found in storage for deletion | public_id={public_id!r}")
        return False
    except Exception as e:
        logger.error(f"Error deleting image from storage | public_id={public_id!r} | error={e}", exc_info=True)
        return False
