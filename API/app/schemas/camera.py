from pydantic import BaseModel
from typing import Optional


# -------------------------
# Camera Creation
# -------------------------

class CameraCreate(BaseModel):
    # rien pour l’instant (créée via user)
    pass


# -------------------------
# Camera Response
# -------------------------

class CameraResponse(BaseModel):
    camera_id: int
    api_key: str


# -------------------------
# Camera Public Info
# -------------------------

class CameraPublic(BaseModel):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
