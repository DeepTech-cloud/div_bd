import firebase_admin
from firebase_admin import credentials, firestore, storage
from pathlib import Path
import logging
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

def init_firebase():
    """Initializes the Firebase Admin SDK."""
    if firebase_admin._apps:
        # Already initialized
        return

    try:
        if settings.FIREBASE_CREDENTIALS_PATH:
            cred_path = Path(settings.FIREBASE_CREDENTIALS_PATH)
            if not cred_path.is_absolute() and not cred_path.exists():
                # Try resolving relative to project root
                project_root = Path(__file__).resolve().parent.parent.parent
                resolved = project_root / settings.FIREBASE_CREDENTIALS_PATH
                if resolved.exists():
                    cred_path = resolved

            cred = credentials.Certificate(str(cred_path))
            
            options = {}
            if settings.FIREBASE_STORAGE_BUCKET:
                options["storageBucket"] = settings.FIREBASE_STORAGE_BUCKET
                
            firebase_admin.initialize_app(cred, options)
            logger.info(f"Firebase Admin SDK initialized successfully with {cred_path}.")
        else:
            # Initialize with default application credentials (e.g. on GCP)
            options = {}
            if settings.FIREBASE_STORAGE_BUCKET:
                options["storageBucket"] = settings.FIREBASE_STORAGE_BUCKET
            firebase_admin.initialize_app(options=options)
            logger.info("Firebase Admin SDK initialized with default credentials.")
            
    except Exception as e:
        logger.critical(f"Failed to initialize Firebase Admin SDK: {e}")

def get_firestore_client():
    return firestore.client()

def get_storage_bucket():
    return storage.bucket()
