import uuid
from pathlib import Path
from PIL import Image
import io
import base64

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from app.core.config import settings
from app.core.firebase import get_storage_bucket
from app.storage.firebase_storage import save_image


class AIGenerator:
    @staticmethod
    def generate_image(
        prompt: str,
        source_image_id: str = "",
        source_image_bytes: bytes | None = None,
    ) -> str:
        """
        Calls the configured Gemini image generation model with the uploaded photo
        and a text prompt to produce a styled/transformed output image.
        Saves result to Firebase Storage and returns an accessible URL.

        Args:
            prompt: The text prompt for generation.
            source_image_id: Firebase Storage path of the source image (used to
                             infer MIME type and as a fallback fetch source).
            source_image_bytes: Pre-downloaded bytes of the source image. When
                                provided, avoids a redundant Firebase fetch.
        """
        # --- Determine MIME type from the image_id extension ---
        mime_type = "image/jpeg"
        if source_image_id:
            if source_image_id.endswith(".png"):
                mime_type = "image/png"
            elif source_image_id.endswith(".webp"):
                mime_type = "image/webp"

        # --- Fetch source image from Firebase only if not already provided ---
        if source_image_bytes is None and source_image_id:
            try:
                bucket = get_storage_bucket()
                blob = bucket.blob(source_image_id)
                if blob.exists():
                    source_image_bytes = blob.download_as_bytes()
            except Exception as e:
                raise RuntimeError(f"Failed to fetch source image from storage: {e}") from e

        if not settings.GEMINI_API_KEY or not genai:
            raise RuntimeError(
                "Gemini API key is not configured. "
                "Set GEMINI_API_KEY in your .env file."
            )

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # --- Build contents: optional image part + text prompt ---
        contents: list = []
        if source_image_bytes:
            image_part = types.Part.from_bytes(
                data=source_image_bytes,
                mime_type=mime_type,
            )
            contents.append(image_part)
        contents.append(prompt)

        # --- Call Gemini ---
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                raise RuntimeError(f"Gemini API quota exceeded: {error_msg}") from e
            if "PERMISSION_DENIED" in error_msg or "API_KEY_INVALID" in error_msg:
                raise RuntimeError(f"Gemini API auth error: {error_msg}") from e
            raise RuntimeError(f"Gemini API error: {error_msg}") from e

        # --- Validate response has candidates ---
        if not response.candidates:
            finish_reason = "unknown"
            if hasattr(response, "prompt_feedback"):
                finish_reason = str(response.prompt_feedback)
            raise RuntimeError(
                f"Gemini returned no candidates (possible safety filter). "
                f"Feedback: {finish_reason}"
            )

        # --- Extract generated image from response ---
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                generated_bytes = part.inline_data.data
                res = save_image(generated_bytes, subfolder="generated", ext="jpg")
                return res["secure_url"]

        # If we get here Gemini responded with only text — treat as failure
        text_parts = [
            p.text for p in response.candidates[0].content.parts
            if hasattr(p, "text") and p.text
        ]
        raise RuntimeError(
            f"Gemini returned no image in response. "
            f"Text parts: {text_parts or '(none)'}"
        )
