from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import JSON

if TYPE_CHECKING:
    from app.models.camera import Camera


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # 🔗 relation caméra
    camera_id: int = Field(foreign_key="camera.id", index=True)

    # 🕒 timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    # 🧠 type d’événement (ex: motion_detected, person_detected)
    type: str = Field(index=True)

    # 📝 description libre
    description: Optional[str] = None

    # ⭐ importance (0 = faible, 1 = normal, 2 = critique)
    importance: int = Field(default=1, index=True)

    # 📦 metadata flexible (vision, bbox, confidence…)
    payload: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )

    # 🔗 relation inverse (optionnelle mais propre)
    camera: Optional["Camera"] = Relationship(back_populates="events")
