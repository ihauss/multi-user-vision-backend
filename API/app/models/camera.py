from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from typing import List
from typing import TYPE_CHECKING

# Avoid circular imports when using type hints for relationships
if TYPE_CHECKING:
    from app.models.event import Event


class Camera(SQLModel, table=True):
    """
    Database model representing a camera entity.

    Attributes:
        id (Optional[int]): Primary key of the camera.
        name (Optional[str]): Optional human-readable name for the camera.
        api_key_hash (str): Hashed API key used for authenticating the camera.
        created_at (datetime): Timestamp of camera creation.
        events (List[Event]): List of events associated with this camera.

    Notes:
        - The API key is never stored in plaintext, only as a hash.
        - Relationships allow ORM-level navigation between Camera and Event.
    """

    # Unique identifier for the camera
    id: Optional[int] = Field(default=None, primary_key=True)

    # Optional display name for easier identification
    name: Optional[str] = None

    # Hashed API key (never store raw API keys)
    api_key_hash: str

    # Timestamp of creation (defaults to current UTC time)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to associated events
    # Allows accessing camera.events to retrieve all related events
    events: List["Event"] = Relationship(back_populates="camera")
