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


# OAuth2 scheme used to extract the Bearer token from incoming requests.
# The token is expected to be provided via the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_user_from_token(token: str, session: Session):
    """
    Decode a JWT token and retrieve the associated user from the database.

    Args:
        token (str): JWT access token.
        session (Session): Database session.

    Returns:
        User: Authenticated user.

    Raises:
        HTTPException:
            - 401 if token is invalid or user does not exist.

    Workflow:
        1. Decode the JWT token.
        2. Extract the user ID from the "sub" claim.
        3. Retrieve the user from the database.

    Notes:
        - The "sub" field is expected to contain the user ID.
        - Token validation (signature, expiration) is handled in decode_access_token.
    """
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user



def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """
    Dependency that returns the currently authenticated user.

    Args:
        token (str): Extracted from Authorization header (Bearer token).
        session (Session): Database session.

    Returns:
        User: Authenticated user.

    Notes:
        - This is the main entry point for authentication in protected routes.
        - It relies on get_user_from_token for validation and retrieval.
    """
    return get_user_from_token(token, session)


@lru_cache()
def get_frame_repository() -> FrameRepository:
    """
    Provide a singleton instance of the frame repository.

    Depending on configuration, this returns either:
        - An in-memory repository (for development/testing)
        - A Redis-backed repository (for production)

    Returns:
        FrameRepository: Concrete implementation of the repository interface.

    Notes:
        - lru_cache ensures that the repository is instantiated only once
          (singleton-like behavior).
        - Environment variables control which backend is used.
        - Redis configuration includes buffer size for frame storage.
    """
    use_redis = os.getenv("USE_REDIS", "false").lower() == "true"

    if not use_redis:
        return InMemoryFrameRepository()

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    max_frames = int(os.getenv("FRAME_BUFFER_SIZE", 10))

    return RedisFrameRepository(
        url=redis_url,
        max_frames=max_frames
    )
