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


class AIGenerator:
    @staticmethod
    def generate_image(prompt: str, source_image_path: str = "") -> str:
        """
        Calls Gemini 2.0 Flash image generation model with the uploaded photo
        and a text prompt to produce a styled/transformed output image.
        Falls back to a placeholder if the API is unavailable.
        Saves result to UPLOAD_DIR/generated/ and returns an accessible URL.
        """
        output_dir = Path(settings.UPLOAD_DIR) / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        gen_filename = f"gen_{uuid.uuid4().hex[:8]}.jpg"
        gen_file_path = output_dir / gen_filename

        if settings.GEMINI_API_KEY and genai:
            try:
                client = genai.Client(api_key=settings.GEMINI_API_KEY)

                # Build contents: image bytes + text prompt
                contents: list = []

                if source_image_path:
                    source_path = Path(source_image_path)
                    if source_path.exists():
                        image_bytes = source_path.read_bytes()

                        # Detect MIME type from extension
                        ext = source_path.suffix.lower()
                        mime_map = {
                            ".jpg": "image/jpeg",
                            ".jpeg": "image/jpeg",
                            ".png": "image/png",
                            ".webp": "image/webp",
                        }
                        mime_type = mime_map.get(ext, "image/jpeg")

                        # Encode image as base64 inline data
                        image_part = types.Part.from_bytes(
                            data=image_bytes,
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
                        with open(gen_file_path, "wb") as f:
                            f.write(generated_bytes)
                        return f"{settings.BASE_URL}/static/generated/{gen_filename}"

                print("Gemini returned no image part in response — falling back.")

            except Exception as e:
                print(f"AI Generation Error (Falling back to placeholder): {e}")

        # --- Fallback: copy sample or create a green placeholder ---
        sample_path = output_dir / "family_blessings_sample.jpg"
        if sample_path.exists() and gen_file_path != sample_path:
            import shutil
            shutil.copy(sample_path, gen_file_path)
        else:
            img = Image.new("RGB", (800, 800), color=(34, 139, 34))
            img.save(gen_file_path, format="JPEG")

        return f"{settings.BASE_URL}/static/generated/{gen_filename}"
