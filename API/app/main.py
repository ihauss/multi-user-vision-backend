from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine

from app.models import User, Camera, CameraUser
from app.api.routes_users import router as user_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"message": "API is running"}


app.include_router(user_router)
