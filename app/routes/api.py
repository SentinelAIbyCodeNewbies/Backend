from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/detect")
def detect(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    key = db.query(models.APIKey).filter(models.APIKey.key == x_api_key).first()

    if not key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    #dummy response 
    return{
        "result": "Fake(demo)",
        "confidence": 0.87
    }