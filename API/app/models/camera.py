from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.event import Event


class Camera(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    api_key_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    events: List["Event"] = Relationship(back_populates="camera")
