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
from app.core.db import SessionLocal
from app.core.models import Image as DBImage
from app.storage.local_storage import save_image


class AIGenerator:
    @staticmethod
    def generate_image(prompt: str, source_image_id: str = "") -> str:
        """
        Calls Gemini 2.0 Flash image generation model with the uploaded photo
        and a text prompt to produce a styled/transformed output image.
        Falls back to a placeholder if the API is unavailable.
        Saves result to PostgreSQL and returns an accessible URL.
        """
        # Fetch the source image from DB if provided
        source_image_bytes = None
        mime_type = "image/jpeg"
        if source_image_id:
            db = SessionLocal()
            try:
                db_image = db.query(DBImage).filter(DBImage.id == source_image_id).first()
                if db_image:
                    source_image_bytes = db_image.content
                    mime_type = db_image.content_type
            finally:
                db.close()

        if settings.GEMINI_API_KEY and genai:
            try:
                client = genai.Client(api_key=settings.GEMINI_API_KEY)

                # Build contents: image bytes + text prompt
                contents: list = []

                if source_image_bytes:
                    image_part = types.Part.from_bytes(
                        data=source_image_bytes,
                        mime_type=mime_type,
                    )
                    contents.append(image_part)

                # Append the text prompt
                contents.append(prompt)

                # Call Gemini 2.5 Flash Image — supports image input + image output
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                    ),
                )

                # Extract the generated image bytes from response
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        generated_bytes = part.inline_data.data
                        res = save_image(generated_bytes, subfolder="generated", ext="jpg")
                        return res["secure_url"]

                print("Gemini returned no image part in response — falling back.")

            except Exception as e:
                print(f"AI Generation Error (Falling back to placeholder): {e}")

        # --- Fallback: copy sample or create a green placeholder ---
        sample_path = Path(settings.UPLOAD_DIR) / "generated" / "family_blessings_sample.jpg"
        if sample_path.exists():
            generated_bytes = sample_path.read_bytes()
        else:
            img = Image.new("RGB", (800, 800), color=(34, 139, 34))
            out_bytes = io.BytesIO()
            img.save(out_bytes, format="JPEG")
            generated_bytes = out_bytes.getvalue()

        res = save_image(generated_bytes, subfolder="generated", ext="jpg")
        return res["secure_url"]

