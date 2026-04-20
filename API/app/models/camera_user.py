from sqlmodel import SQLModel, Field
from typing import Optional


class CameraUser(SQLModel, table=True):
    """
    Association table linking users to cameras with a specific role.

    This model represents a many-to-many relationship between:
        - Users
        - Cameras

    Attributes:
        user_id (int): ID of the user.
        camera_id (int): ID of the camera.
        role (str): Role of the user for this camera ("owner" or "viewer").

    Notes:
        - Composite primary key ensures uniqueness of (user_id, camera_id).
        - Used for access control (RBAC).
        - Roles define permissions on the camera.
    """

    # Foreign key referencing the user
    # Part of composite primary key
    user_id: int = Field(foreign_key="user.id", primary_key=True)

    # Foreign key referencing the camera
    # Part of composite primary key
    camera_id: int = Field(foreign_key="camera.id", primary_key=True)

    # Role assigned to the user for this camera
    # Default role is "viewer"
    role: str = Field(default="viewer")  # Possible values: "owner", "viewer"
