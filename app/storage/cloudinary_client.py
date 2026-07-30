# This module has been replaced by local_storage.py
# Cloudinary integration was removed in favour of local filesystem storage.
# See app/storage/local_storage.py for save_image() and delete_image().
raise ImportError(
    "cloudinary_client is no longer used. Import from app.storage.local_storage instead."
)
