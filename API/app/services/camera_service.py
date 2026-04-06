import secrets
from passlib.context import CryptContext
from sqlmodel import Session

from app.models import Camera, CameraUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_api_key():
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    return pwd_context.hash(api_key)


def create_camera(session: Session, user_id: int):
    # 1. generate key
    raw_key = generate_api_key()
    hashed_key = hash_api_key(raw_key)

    # 2. create camera
    camera = Camera(api_key_hash=hashed_key)
    session.add(camera)
    session.commit()
    session.refresh(camera)

    # 3. link owner
    link = CameraUser(
        user_id=user_id,
        camera_id=camera.id,
        role="owner"
    )
    session.add(link)
    session.commit()

    return camera, raw_key
