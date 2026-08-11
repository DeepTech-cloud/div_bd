from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.models import Setting

router = APIRouter()

@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    settings_records = db.query(Setting).all()
    return {record.key: record.value for record in settings_records}

@router.put("/")
def update_settings(payload: dict, db: Session = Depends(get_db)):
    for key, value in payload.items():
        db_setting = db.query(Setting).filter(Setting.key == key).first()
        if db_setting:
            db_setting.value = value
        else:
            db_setting = Setting(key=key, value=value)
            db.add(db_setting)
    db.commit()
    return {"message": "Settings updated successfully"}

