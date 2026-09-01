import uuid
import datetime
from app.core.firebase import get_storage_bucket

def save_image(file_bytes: bytes, subfolder: str = "uploads", ext: str = "jpg") -> dict:
    """
    Saves raw image bytes to Firebase Storage.
    Returns a dict compatible with the expected response shape.
    """
    filename = f"{uuid.uuid4().hex}.{ext}"
    rel_path = f"{subfolder}/{filename}"
    
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
    blob.upload_from_string(file_bytes, content_type=content_type)
    
    # Try to make the blob publicly accessible.
    # This fails on buckets with Uniform bucket-level access — fall back to a signed URL.
    try:
        blob.make_public()
        public_url = blob.public_url
    except Exception:
        import datetime
        public_url = blob.generate_signed_url(
            expiration=datetime.timedelta(days=7),
            method="GET",
            version="v4",
        )

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
    try:
        bucket = get_storage_bucket()
        blob = bucket.blob(public_id)
        if blob.exists():
            blob.delete()
            return True
        return False
    except Exception:
        return False
