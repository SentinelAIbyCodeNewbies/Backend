from fastapi import APIRouter, Header, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models
from app.auth import get_current_user
from app.schemas import AnalyseRequest
from app.services.video_detector import predict_video
from app.services.downloader import download_file
import os

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
        try:
            temp_path = "test.mp4"
            
            prediction = predict_video(temp_path)

            result = prediction["prediction"]
            confidence = str(prediction["confidence"])

            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/analyse_upload")
async def analyse_upload(
    file: UploadFile = File(...),
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    key = db.query(models.APIKey).filter(models.APIKey.key == x_api_key).first()

    if not key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        temp_path = f"temp_{file.filename}"

        with open(temp_path, "wb") as f:
            f.write(await file.read())

        prediction = predict_video(temp_path)

        result = prediction["prediction"]
        confidence = str(prediction["confidence"])

        scan = models.Scan(
            user_id = key.user_id,
            input_data = file.filename,
            result = result,
            confidence = confidence
        )
        db.add(scan)
        db.commit()

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return{
            "type": "video",
            "result": result,
            "confidence": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_history(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    scans = db.query(models.Scan).filter(models.Scan.user_id == user_id)\
        .order_by(models.Scan.created_at.desc()).all()

    return scans