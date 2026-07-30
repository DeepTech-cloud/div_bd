import uuid
import shutil
from pathlib import Path
from app.core.config import settings

# Ensure upload directories exist on startup
_UPLOAD_DIR = Path(settings.UPLOAD_DIR)
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(_UPLOAD_DIR / "uploads").mkdir(exist_ok=True)
(_UPLOAD_DIR / "generated").mkdir(exist_ok=True)


def save_image(file_bytes: bytes, subfolder: str = "uploads", ext: str = "jpg") -> dict:
    """
    Saves raw image bytes to the local filesystem.
    Returns a dict compatible with the old Cloudinary response shape.
    """
    filename = f"{uuid.uuid4().hex}.{ext}"
    rel_path = f"{subfolder}/{filename}"
    dest = _UPLOAD_DIR / rel_path
    dest.write_bytes(file_bytes)

    # Build a public URL served by FastAPI's StaticFiles mount at /static
    public_url = f"{settings.BASE_URL}/static/{rel_path}"

    return {
        "secure_url": public_url,
        "public_id": rel_path,   # used as the deletion key
        "width": None,
        "height": None,
        "format": ext,
    }


def delete_image(public_id: str) -> bool:
    """
    Deletes a locally stored image by its public_id (relative path).
    Returns True on success, False if the file was not found.
    """
    target = _UPLOAD_DIR / public_id
    if target.exists():
        target.unlink()
        return True
    return False
