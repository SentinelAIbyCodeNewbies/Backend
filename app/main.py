from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, api, news
from app.db import Base, engine

app = FastAPI(title="Sentinel AI", version="1.0.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router,prefix="/auth", tags=["Auth"])
app.include_router(api.router, tags=["API"])
app.include_router(news.router, tags=["News"])

@app.get("/")
def root():
    return {"message": "Sentinel AI backend running"}
