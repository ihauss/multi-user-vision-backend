import secrets
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models import Camera, CameraUser, User


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


def add_user_to_camera(
    session: Session,
    camera_id: int,
    target_username: str,
    current_user: User,
):
    # 🔍 récupérer caméra
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # 🔐 vérifier ownership
    link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id,
            CameraUser.role == "owner"
        )
    ).first()

    if not link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 🔍 récupérer user cible
    statement = select(User).where(User.username == target_username)
    target_user = session.exec(statement).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🚫 éviter doublon
    statement = select(CameraUser).where(
        CameraUser.camera_id == camera_id,
        CameraUser.user_id == target_user.id
    )
    existing = session.exec(statement).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already added")

    # ✅ création lien
    link = CameraUser(
        camera_id=camera_id,
        user_id=target_user.id,
        role="viewer"
    )

    session.add(link)
    session.commit()

    return {"message": "User added to camera"}


def remove_user_from_camera(session, camera_id, username, current_user):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # ✅ Vérifier owner
    owner_link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id,
            CameraUser.role == "owner"
        )
    ).first()

    if not owner_link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 🔍 Trouver user
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🚫 Empêcher de supprimer un owner
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")

    # 🔍 Vérifier lien
    link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == user.id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="User not in camera")

    session.delete(link)
    session.commit()

    return {"message": "User removed"}


def delete_camera(session, camera_id, current_user):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # ✅ vérifier owner
    owner_link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id,
            CameraUser.role == "owner"
        )
    ).first()

    if not owner_link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 🧹 supprimer toutes les relations
    links = session.exec(
        select(CameraUser).where(CameraUser.camera_id == camera_id)
    ).all()

    for link in links:
        session.delete(link)

    # 🗑 supprimer la caméra
    session.delete(camera)

    session.commit()

    return {"message": "Camera deleted"}
