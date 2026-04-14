from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.database import engine
from app.models import User, Camera, CameraUser, Event
from app.api.routes_users import router as user_router
from app.api.routes_cameras import router as camera_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Starting app")
    SQLModel.metadata.create_all(engine)

    yield

    # shutdown
    print("Stopping app")


app = FastAPI(lifespan=lifespan)  # 🔥 IMPORTANT

app.include_router(user_router)
app.include_router(camera_router)
