from fastapi import HTTPException
from sqlmodel import select
from passlib.context import CryptContext

from app.models import Camera, CameraUser
from app.services.utils import verify_api_key, pwd_context


def verify_api_key(api_key: str, hashed: str) -> bool:
    return pwd_context.verify(api_key, hashed)


def push_frame(session, api_key: str, data: str, repo):
    cameras = session.exec(select(Camera)).all()

    camera = None
    for cam in cameras:
        if verify_api_key(api_key, cam.api_key_hash):
            camera = cam
            break

    if not camera:
        raise HTTPException(status_code=401, detail="Invalid API key")

    repo.save(camera.id, data)

    return {"message": "Frame received"}


def get_last_frame(session, camera_id: int, current_user, repo):
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
    frame = repo.get(camera_id)

    if not frame:
        return {"data": None}

    return {"data": frame}
