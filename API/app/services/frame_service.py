from fastapi import HTTPException
from sqlmodel import select
from passlib.context import CryptContext

from app.models import Camera, CameraUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔥 stockage temporaire (remplacé par Redis plus tard)
FRAME_STORE = {}


def verify_api_key(api_key: str, hashed: str) -> bool:
    return pwd_context.verify(api_key, hashed)


def push_frame(session, api_key: str, data: str):
    cameras = session.exec(select(Camera)).all()

    camera = None
    for cam in cameras:
        if verify_api_key(api_key, cam.api_key_hash):
            camera = cam
            break

    if not camera:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 📡 Stockage (temporaire)
    if camera.id not in FRAME_STORE:
        FRAME_STORE[camera.id] = []
    FRAME_STORE[camera.id].append(data)

    return {"message": "Frame received"}


def get_last_frame(session, camera_id: int, current_user):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # 🔐 vérifier accès (owner OU viewer)
    link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 📡 récupérer dernière frame
    frames = FRAME_STORE.get(camera_id, [])

    if not frames:
        return {"data": None}

    return {"data": frames[-1]}
