import uuid
from app.core.config import settings
from app.core.db import SessionLocal
from app.core.models import Image

def save_image(file_bytes: bytes, subfolder: str = "uploads", ext: str = "jpg") -> dict:
    """
    Saves raw image bytes to the PostgreSQL database.
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

    # Build a public URL served by our custom static route at /static
    public_url = f"{settings.BASE_URL}/static/{rel_path}"

    db = SessionLocal()
    try:
        db_image = Image(
            id=rel_path,
            content=file_bytes,
            content_type=content_type
        )
        db.add(db_image)
        db.commit()
    finally:
        db.close()

    return {
        "secure_url": public_url,
        "public_id": rel_path,   # used as the deletion key
        "width": None,
        "height": None,
        "format": ext,
    }


def delete_image(public_id: str) -> bool:
    """
    Deletes an image from the database by its public_id.
    Returns True on success, False if the image was not found.
    """
    db = SessionLocal()
    try:
        db_image = db.query(Image).filter(Image.id == public_id).first()
        if db_image:
            db.delete(db_image)
            db.commit()
            return True
        return False
    finally:
        db.close()

