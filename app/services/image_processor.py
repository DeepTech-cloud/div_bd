import asyncio
import logging
import os
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=4)


class ImageProcessor:
    @staticmethod
    def process(image_bytes: bytes) -> bytes:
        """
        Processes the image: Compress, Resize, Face Detection check,
        Orientation Fix, Noise Reduction.

        NOTE: cv2.fastNlMeansDenoisingColored is CPU-intensive (5–30s).
        Run this in a thread pool if calling from an async context:
            await asyncio.get_event_loop().run_in_executor(
                _executor, ImageProcessor.process, image_bytes
            )
        """
        logger.info(f"Processing image | input_size={len(image_bytes)} bytes")

        # 1. Load image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            logger.warning("Failed to decode image bytes")
            raise ValueError("Invalid image")
        logger.debug(f"Image decoded | shape={img.shape}")

        # 2. Noise Reduction (FastNlMeansDenoising — CPU-intensive)
        logger.debug("Applying noise reduction (fastNlMeansDenoisingColored)...")
        img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        logger.debug("Noise reduction complete")

        # 3. Face Detection (Simple Haar Cascade check)
        logger.debug("Running face detection...")
        cascade_path = os.environ.get(
            "HAAR_CASCADE_PATH",
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml",
        )
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if face_cascade.empty():
            logger.error(f"Failed to load Haar cascade from: {cascade_path}")
            raise RuntimeError(
                f"Face detection model not found at '{cascade_path}'. "
                "Ensure HAAR_CASCADE_PATH is set correctly in the container."
            )
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) == 0:
            logger.warning("No face detected in image")
            raise ValueError("No face detected in the image. Please upload a clear photo with a visible face.")
        logger.info(f"Face detection passed | faces_found={len(faces)}")

        # 4. Resize if too large (Max width 1920)
        max_width = 1920
        height, width = img.shape[:2]
        if width > max_width:
            ratio = max_width / width
            new_dim = (max_width, int(height * ratio))
            img = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)
            logger.debug(f"Image resized | original={width}x{height} -> {new_dim[0]}x{new_dim[1]}")

        # 5. Compress and return JPEG bytes (always JPEG regardless of input format)
        is_success, buffer = cv2.imencode(
            ".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 85]
        )
        if not is_success:
            logger.error("Failed to encode image to JPEG")
            raise ValueError("Failed to encode image")

        result = buffer.tobytes()
        logger.info(f"Image processing complete | output_size={len(result)} bytes")
        return result

    @staticmethod
    async def process_async(image_bytes: bytes) -> bytes:
        """Async wrapper — runs the blocking process() in a thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, ImageProcessor.process, image_bytes)
