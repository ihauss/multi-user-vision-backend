from sqlmodel import Session, select
from fastapi import HTTPException
from app.models import Event, Camera, CameraUser
from app.services.utils import verify_api_key


def create_event(session: Session, api_key: str, data: dict):
    # 🔐 vérifier caméra via API key
    cam = session.get(Camera, data["camera_id"])

    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    if not verify_api_key(api_key, cam.api_key_hash):
        raise HTTPException(status_code=401, detail="Invalid API key")

    event = Event(
        camera_id=cam.id,
        type=data["type"],
        description=data.get("description"),
        importance=data.get("importance", 1),
        payload=data.get("payload"),
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return {"id": event.id}


def get_events(session: Session, camera_id: int, current_user):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # 🔐 check accès
    link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=403, detail="Not authorized")

    events = session.exec(
        select(Event).where(Event.camera_id == camera_id)
    ).all()

    return events
