from fastapi import HTTPException
from sqlmodel import select
from passlib.context import CryptContext

from app.models import Camera, CameraUser
from app.services.utils import verify_api_key, pwd_context


def verify_api_key(api_key: str, hashed: str) -> bool:
    """
    Verify a raw API key against its hashed version.

    Args:
        api_key (str): Raw API key provided by the client.
        hashed (str): Hashed API key stored in the database.

    Returns:
        bool: True if the API key matches the hash, False otherwise.

    Notes:
        - Uses bcrypt verification via passlib.
        - This is a secure comparison resistant to timing attacks.
    """
    return pwd_context.verify(api_key, hashed)


def push_frame(session, api_key: str, data: str, repo):
    """
    Store a new frame associated with a camera identified by an API key.

    Args:
        session (Session): Database session.
        api_key (str): Raw API key provided in the request.
        data (str): Frame data (e.g., base64 encoded image or serialized payload).
        repo: Frame repository (e.g., Redis) used for fast storage.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException:
            - 401 if the API key is invalid.

    Workflow:
        1. Retrieve all cameras from the database.
        2. Iterate through cameras and verify the API key against each stored hash.
        3. Identify the matching camera.
        4. Store the frame in the repository using the camera ID.

    Notes:
        - This implementation performs a linear scan over all cameras.
        - API keys are never stored in plaintext.
        - The repository is expected to provide a fast in-memory storage layer.
    """
    # Retrieve all cameras from the database
    cameras = session.exec(select(Camera)).all()

    camera = None

    # Find the camera matching the provided API key
    for cam in cameras:
        if verify_api_key(api_key, cam.api_key_hash):
            camera = cam
            break

    # Reject if no matching camera is found
    if not camera:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Store the frame in the repository (e.g., Redis)
    repo.save(camera.id, data)

    return {"message": "Frame received"}


def get_last_frame(session, camera_id: int, current_user, repo):
    """
    Retrieve the latest frame for a given camera.

    Args:
        session (Session): Database session.
        camera_id (int): ID of the camera.
        current_user (User): Authenticated user requesting the frame.
        repo: Frame repository (e.g., Redis).

    Returns:
        dict:
            - data: The latest frame or None if no frame is available.

    Raises:
        HTTPException:
            - 404 if camera does not exist.
            - 403 if user does not have access.

    Workflow:
        1. Verify that the camera exists.
        2. Check if the user is associated with the camera.
        3. Retrieve the latest frame from the repository.

    Notes:
        - Access is granted to both owners and viewers.
        - Frames are stored in a fast-access storage (e.g., Redis).
    """
    # Check if camera exists
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Verify user access (owner or viewer)
    link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Retrieve latest frame from repository
    frame = repo.get(camera_id)

    if not frame:
        return {"data": None}

    return {"data": frame}
