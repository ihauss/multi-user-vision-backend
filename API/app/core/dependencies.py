import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session
from functools import lru_cache

from app.database import get_session
from app.models.user import User
from app.core.security import decode_access_token
from app.repositories.in_memory_frame_repository import InMemoryFrameRepository
from app.repositories.redis_frame_repository import RedisFrameRepository
from app.repositories.frame_repository import FrameRepository
from app.core.config import USE_REDIS


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@lru_cache()
def get_frame_repository() -> FrameRepository:
    use_redis = os.getenv("USE_REDIS", "false").lower() == "true"

    if not use_redis:
        return InMemoryFrameRepository()

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    max_frames = int(os.getenv("FRAME_BUFFER_SIZE", 10))

    return RedisFrameRepository(
        url=redis_url,
        max_frames=max_frames
    )
