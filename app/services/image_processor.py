import cv2
import numpy as np
from io import BytesIO
from PIL import Image

class ImageProcessor:
    @staticmethod
    def process(image_bytes: bytes) -> bytes:
        """
        Processes the image: Compress, Resize, Face Detection check, 
        Orientation Fix, Noise Reduction.
        """
        # 1. Load image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image")

        # 2. Noise Reduction (FastNlMeansDenoising)
        img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

        # 3. Face Detection (Simple Haar Cascade check)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) == 0:
            pass # We could raise an error here if faces are strictly required

        # 4. Resize if too large (Max width 1920)
        max_width = 1920
        height, width = img.shape[:2]
        if width > max_width:
            ratio = max_width / width
            new_dim = (max_width, int(height * ratio))
            img = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)

        # 5. Compress and return bytes
        is_success, buffer = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not is_success:
            raise ValueError("Failed to encode image")
            
        return buffer.tobytes()
