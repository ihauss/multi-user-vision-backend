from pydantic import BaseModel
from typing import Optional


# -------------------------
# Add User to Camera
# -------------------------

class CameraUserAdd(BaseModel):
    """
    Schema used to add a user to a camera.

    Attributes:
        username (str): Username of the user to add.
        role (Optional[str]): Role assigned to the user ("viewer" by default).

    Notes:
        - Role defines access level (e.g., "owner", "viewer").
        - Should ideally be validated to restrict allowed values.
    """
    username: str
    role: Optional[str] = "viewer"


# -------------------------
# Camera User Response
# -------------------------

class CameraUserResponse(BaseModel):
    """
    Response schema representing a user-camera association.

    Attributes:
        user_id (int): ID of the user.
        camera_id (int): ID of the camera.
        role (str): Role assigned to the user.

    Notes:
        - Used when returning camera-user relationships via API.
        - Compatible with ORM objects via `from_attributes`.
    """
    user_id: int
    camera_id: int
    role: str

    class Config:
        # Enables automatic conversion from ORM objects (SQLModel)
        from_attributes = True
