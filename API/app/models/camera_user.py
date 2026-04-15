from sqlmodel import SQLModel, Field
from typing import Optional


class CameraUser(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    camera_id: int = Field(foreign_key="camera.id", primary_key=True)
    role: str = Field(default="viewer")  # "owner", "viewer"
