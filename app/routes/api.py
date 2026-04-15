from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models
from app.auth import get_current_user
from app.schemas import AnalyseRequest

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyse")
def analyse(
    request: AnalyseRequest,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):

    key = db.query(models.APIKey).filter(models.APIKey.key == x_api_key).first()

    if not key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    input_type = request.type
    input_data = request.input

    if input_type == "image":
        result = "fake"
        confidence = "0.91"
    elif input_type == "video":
        result = "real"
        confidence = "0.76"

    elif input_type == "audio":
        result = "fake"
        confidence = "0.82"

    elif input_type == "url":
        result = "fake"
        confidence = "0.88"
    else:
        raise HTTPException(status_code=400, detail="Invalid Type")

    scan = models.Scan(
        user_id=key.user_id,
        input_data=input_data,
        result=result,
        confidence=confidence
    )
    db.add(scan)
    db.commit()

    return {
        "type": input_type,
        "result": result,
        "confidence": confidence
    }

@router.get("/history")
def get_history(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    scans = db.query(models.Scan).filter(models.Scan.user_id == user_id)\
        .order_by(models.Scan.created_at.desc()).all()

    return scans