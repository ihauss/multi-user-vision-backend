from pydantic import BaseModel
from typing import Optional


# -------------------------
# Camera Creation
# -------------------------

class CameraCreate(BaseModel):
    """
    Schema used for camera creation.

    Currently empty because cameras are created implicitly
    for the authenticated user.

    Notes:
        - This can be extended later (e.g., name, metadata).
    """
    pass


# -------------------------
# Camera Response
# -------------------------

class CameraResponse(BaseModel):
    """
    Response schema returned after creating a camera.

    Attributes:
        camera_id (int): Unique identifier of the camera.
        api_key (str): API key used by the camera/device to authenticate.

    Notes:
        - The API key is only returned once at creation time.
        - It should be securely stored by the client.
    """
    camera_id: int
    api_key: str


# -------------------------
# Camera Public Info
# -------------------------

class CameraPublic(BaseModel):
    """
    Public representation of a camera.

    Attributes:
        id (int): Camera ID.
        owner_id (int): ID of the owner.

    Notes:
        - Used when exposing camera data to clients.
        - Does not include sensitive information (e.g., API key).
    """
    id: int
    owner_id: int

    class Config:
        # Enables compatibility with ORM objects (SQLModel)
        from_attributes = True


class AddUserRequest(BaseModel):
    """
    Schema for adding a user to a camera.

    Attributes:
        username (str): Username of the user to add.
    """
    username: str
