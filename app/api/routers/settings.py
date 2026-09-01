from fastapi import APIRouter, HTTPException
from app.core.firebase import get_firestore_client

router = APIRouter()

@router.get("/")
def get_settings():
    try:
        db = get_firestore_client()
        settings_ref = db.collection("settings")
        docs = settings_ref.stream()
        
        settings = {}
        for doc in docs:
            doc_dict = doc.to_dict()
            if "value" in doc_dict:
                settings[doc.id] = doc_dict["value"]
                
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {e}")

@router.put("/")
def update_settings(payload: dict):
    try:
        db = get_firestore_client()
        settings_ref = db.collection("settings")
        
        batch = db.batch()
        for key, value in payload.items():
            doc_ref = settings_ref.document(key)
            batch.set(doc_ref, {"value": value}, merge=True)
            
        batch.commit()
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {e}")
