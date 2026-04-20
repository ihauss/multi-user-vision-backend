from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.database import engine
from app.models import User, Camera, CameraUser, Event
from app.api.routes_users import router as user_router
from app.api.routes_cameras import router as camera_router
from app.api import routes_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    This function is executed:
        - Once at startup
        - Once at shutdown

    Args:
        app (FastAPI): FastAPI application instance.

    Behavior:
        - On startup:
            - Initializes the database schema.
        - On shutdown:
            - Performs cleanup (if needed).

    Notes:
        - This replaces older @app.on_event("startup") patterns.
        - Ensures proper lifecycle management in async environments.
    """
    # Startup phase
    print("Starting app")

    # Create all database tables if they do not exist
    # (based on SQLModel metadata)
    SQLModel.metadata.create_all(engine)

    yield

    # Shutdown phase
    print("Stopping app")


# Initialize FastAPI application with lifecycle management
app = FastAPI(lifespan=lifespan)


# Register API routers
# Each router handles a specific domain of the application
app.include_router(user_router)
app.include_router(camera_router)
app.include_router(routes_events.router)
