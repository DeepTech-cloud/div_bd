import logging
from fastapi import APIRouter, HTTPException
from app.core.firebase import get_firestore_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def get_settings():
    logger.info("Fetching settings from Firestore")
    try:
        db = get_firestore_client()
        settings_ref = db.collection("settings")
        docs = settings_ref.stream()
        
        settings = {}
        for doc in docs:
            doc_dict = doc.to_dict()
            if "value" in doc_dict:
                settings[doc.id] = doc_dict["value"]

        logger.info(f"Settings fetched | keys={list(settings.keys())}")
        return settings
    except Exception as e:
        logger.error(f"Failed to fetch settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {e}")

@router.put("/")
def update_settings(payload: dict):
    logger.info(f"Update settings request | keys={list(payload.keys())}")
    try:
        db = get_firestore_client()
        settings_ref = db.collection("settings")
        
        batch = db.batch()
        for key, value in payload.items():
            doc_ref = settings_ref.document(key)
            batch.set(doc_ref, {"value": value}, merge=True)
            
        batch.commit()
        logger.info(f"Settings updated successfully | keys={list(payload.keys())}")
        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {e}")
