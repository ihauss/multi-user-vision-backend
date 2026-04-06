from pydantic import BaseModel


class FrameCreate(BaseModel):
    data: str  # base64 ou string simple pour tests


class FrameResponse(BaseModel):
    camera_id: int
    data: str
