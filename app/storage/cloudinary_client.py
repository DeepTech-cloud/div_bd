# This module has been replaced by firebase_storage.py
# Cloudinary integration was removed in favour of Firebase Storage.
# See app/storage/firebase_storage.py for save_image() and delete_image().
raise ImportError(
    "cloudinary_client is no longer used. Import from app.storage.firebase_storage instead."
)
