import base64
import logging
from fastapi import APIRouter, Request, HTTPException
from app.services.image_processor import ImageProcessor
from app.storage.firebase_storage import save_image
from app.schemas.image import UploadResponse

logger = logging.getLogger(__name__)
router = APIRouter()

IMAGE_MAGIC_BYTES = (
    b"\xff\xd8\xff",       # JPEG
    b"\x89PNG\r\n\x1a\n",  # PNG
    b"GIF87a",             # GIF
    b"GIF89a",             # GIF
    b"RIFF",               # WebP
    b"BM",                 # BMP
)


def _is_image_bytes(data: bytes) -> bool:
    """Checks if raw bytes start with valid image magic headers."""
    if not data or len(data) < 4:
        return False
    return any(data.startswith(magic) for magic in IMAGE_MAGIC_BYTES)


@router.post("", response_model=UploadResponse)
@router.post("/", response_model=UploadResponse)
async def upload_image_endpoint(request: Request):
    """
    Universal image upload endpoint. Accepts images via:
    1. Multipart/form-data with ANY field name ('file', 'image', 'photo', 'picture', etc.)
    2. JSON body: {"image": "..."} or {"image_base64": "..."} or {"file": "..."}
    3. Raw binary body (image/jpeg, image/png, application/octet-stream)
    """
    contents: bytes | None = None
    content_type = request.headers.get("content-type", "").lower()
    logger.info(f"Upload request received | content-type={content_type!r}")

    # --- 1. Multipart Form Data (any key name) ---
    if "multipart/form-data" in content_type:
        try:
            form = await request.form()
            # Check all values in the form
            for val in form.values():
                if hasattr(val, "read"):
                    raw = await val.read()
                    if raw:
                        contents = raw
                        logger.debug(f"Multipart: extracted {len(raw)} bytes from file field")
                        break
                elif isinstance(val, str):
                    b64_part = val.split(",", 1)[1] if "," in val else val
                    try:
                        decoded = base64.b64decode(b64_part)
                        if _is_image_bytes(decoded):
                            contents = decoded
                            logger.debug(f"Multipart: extracted {len(decoded)} bytes from base64 field")
                            break
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Failed to parse multipart form: {e}")
            raise HTTPException(status_code=422, detail=f"Failed to parse multipart form: {e}")

    # --- 2. JSON Payload (base64 string) ---
    elif "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                for key in ("image", "image_base64", "file", "photo", "data", "img", "content", "picture"):
                    val = body.get(key)
                    if isinstance(val, str) and val:
                        b64_part = val.split(",", 1)[1] if "," in val else val
                        contents = base64.b64decode(b64_part)
                        logger.debug(f"JSON: extracted {len(contents)} bytes from field '{key}'")
                        break
                if not contents:
                    for val in body.values():
                        if isinstance(val, str) and len(val) > 100:
                            b64_part = val.split(",", 1)[1] if "," in val else val
                            try:
                                decoded = base64.b64decode(b64_part)
                                if _is_image_bytes(decoded):
                                    contents = decoded
                                    logger.debug(f"JSON: extracted {len(decoded)} bytes from fallback field")
                                    break
                            except Exception:
                                pass
        except Exception as e:
            logger.warning(f"Invalid JSON body: {e}")
            raise HTTPException(status_code=422, detail=f"Invalid JSON body: {e}")

    # --- 3. Raw Binary Payload or Fallback ---
    if not contents:
        raw_body = await request.body()
        if raw_body and _is_image_bytes(raw_body):
            contents = raw_body
            logger.debug(f"Raw binary: extracted {len(raw_body)} bytes")

    if not contents:
        logger.warning("Upload rejected: no image bytes found in request")
        raise HTTPException(
            status_code=422,
            detail=(
                "No image found in request. Please upload using:\n"
                "1. Multipart form-data with any file field (e.g. 'file', 'image')\n"
                "2. JSON body: {\"image\": \"<base64 string>\"}\n"
                "3. Raw binary image body with Content-Type 'image/jpeg' or 'image/png'"
            )
        )

    logger.info(f"Image bytes received: {len(contents)} bytes — starting processing")
    try:
        # Process Image in thread pool (denoising, resizing, face cascade)
        processed_bytes = await ImageProcessor.process_async(contents)
        logger.info(f"Image processing complete: {len(processed_bytes)} bytes")

        # Save to Firebase Storage
        upload_result = save_image(processed_bytes, subfolder="uploads", ext="jpg")
        logger.info(f"Image saved to Firebase | image_id={upload_result['public_id']} | url={upload_result['secure_url']}")

        return UploadResponse(
            image_id=upload_result["public_id"],
            image_url=upload_result["secure_url"]
        )
    except ValueError as e:
        logger.warning(f"Image validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {e}")
