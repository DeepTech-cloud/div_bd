import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
IMAGE_PATH = sys.argv[1] if len(sys.argv) > 1 else "dummy.jpg"

CUSTOM_PROMPT = sys.argv[2] if len(sys.argv) > 2 else None

if not os.path.exists(IMAGE_PATH):
    print(f"Error: image file '{IMAGE_PATH}' not found.")
    sys.exit(1)

print(f"Uploading image: {IMAGE_PATH} -> {BASE_URL}/api/v1/upload")
with open(IMAGE_PATH, "rb") as f:
    fname = os.path.basename(IMAGE_PATH)
    files = {"file": (fname, f, "image/jpeg")}
    res_upload = requests.post(f"{BASE_URL}/api/v1/upload", files=files)

print("Upload response:", res_upload.status_code, res_upload.text)

if res_upload.status_code == 200:
    data = res_upload.json()
    image_id = data.get("image_id")
    print(f"Got image_id: {image_id}")

    print("Requesting generation...")
    payload = {"image_id": image_id}
    if CUSTOM_PROMPT:
        payload["prompt"] = CUSTOM_PROMPT
        print(f"Using custom prompt: {CUSTOM_PROMPT}")

    res_gen = requests.post(
        f"{BASE_URL}/api/v1/generate",
        json=payload
    )
    print("Generate response:", res_gen.status_code, res_gen.text)
