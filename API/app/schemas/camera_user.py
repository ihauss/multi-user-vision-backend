from pydantic import BaseModel
from typing import Optional


# -------------------------
# Add User to Camera
# -------------------------

class CameraUserAdd(BaseModel):
    username: str
    role: Optional[str] = "viewer"


# -------------------------
# Camera User Response
# -------------------------

class CameraUserResponse(BaseModel):
    user_id: int
    camera_id: int
    role: str

    class Config:
        from_attributes = True
