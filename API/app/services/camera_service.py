import secrets
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models import Camera, CameraUser, User


# Password hashing context used to hash API keys securely.
# Uses bcrypt, which is a strong adaptive hashing algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_api_key():
    """
    Generate a secure random API key.

    Returns:
        str: A URL-safe random string suitable for use as an API key.

    Notes:
        - Uses Python's `secrets` module, which is cryptographically secure.
        - The length (32 bytes) provides strong entropy.
    """
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key before storing it in the database.

    Args:
        api_key (str): Raw API key.

    Returns:
        str: Hashed API key.

    Notes:
        - Hashing prevents storing sensitive keys in plaintext.
        - Even if the database is compromised, raw keys cannot be retrieved.
    """
    return pwd_context.hash(api_key)


def create_camera(session: Session, user_id: int):
    """
    Create a new camera and assign ownership to a user.

    Args:
        session (Session): Database session.
        user_id (int): ID of the user creating the camera.

    Returns:
        tuple:
            - Camera: The created camera object.
            - str: The raw API key (returned only once).

    Workflow:
        1. Generate a secure API key.
        2. Hash the API key and store it in the database.
        3. Create the camera record.
        4. Link the user as the owner of the camera.

    Notes:
        - The raw API key is returned only at creation time.
        - It should never be stored or logged after this point.
    """
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
    """
    Add a user to a camera with viewer access.

    Args:
        session (Session): Database session.
        camera_id (int): ID of the camera.
        target_username (str): Username of the user to add.
        current_user (User): Authenticated user performing the action.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException:
            - 404 if camera or user is not found.
            - 403 if current user is not the owner.
            - 400 if user is already associated with the camera.

    Notes:
        - Only the camera owner can add users.
        - Newly added users are assigned the "viewer" role.
    """
    # Retrieve camera
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Verify ownership
    link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id,
            CameraUser.role == "owner"
        )
    ).first()

    if not link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Retrieve target user
    statement = select(User).where(User.username == target_username)
    target_user = session.exec(statement).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent duplicate association
    statement = select(CameraUser).where(
        CameraUser.camera_id == camera_id,
        CameraUser.user_id == target_user.id
    )
    existing = session.exec(statement).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already added")

    # Create association
    link = CameraUser(
        camera_id=camera_id,
        user_id=target_user.id,
        role="viewer"
    )

    session.add(link)
    session.commit()

    return {"message": "User added to camera"}


def remove_user_from_camera(session, camera_id, username, current_user):
    """
    Remove a user from a camera.

    Args:
        session (Session): Database session.
        camera_id (int): ID of the camera.
        username (str): Username of the user to remove.
        current_user (User): Authenticated user.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException:
            - 404 if camera or user is not found.
            - 403 if current user is not the owner.
            - 400 if attempting to remove oneself.
            - 404 if user is not linked to the camera.

    Notes:
        - Only the camera owner can remove users.
        - Owners cannot remove themselves to prevent orphaned cameras.
    """
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Verify ownership
    owner_link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id,
            CameraUser.role == "owner"
        )
    ).first()

    if not owner_link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Retrieve target user
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent removing oneself (owner)
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")

    # Check if association exists
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
    """
    Delete a camera and all associated user relationships.

    Args:
        session (Session): Database session.
        camera_id (int): ID of the camera.
        current_user (User): Authenticated user.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException:
            - 404 if camera not found.
            - 403 if user is not the owner.

    Notes:
        - This operation removes all CameraUser relationships first.
        - The camera is then permanently deleted.
    """
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Verify ownership
    owner_link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id,
            CameraUser.role == "owner"
        )
    ).first()

    if not owner_link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete all relationships
    links = session.exec(
        select(CameraUser).where(CameraUser.camera_id == camera_id)
    ).all()

    for link in links:
        session.delete(link)

    # Delete camera
    session.delete(camera)
    session.commit()

    return {"message": "Camera deleted"}


def check_camera_access(session, camera_id: int, user_id: int):
    """
    Check whether a user has access to a given camera.

    Args:
        session (Session): Database session.
        camera_id (int): ID of the camera.
        user_id (int): ID of the user.

    Raises:
        HTTPException:
            - 403 if the user does not have access.

    Notes:
        - This function is used for access control across endpoints.
        - It verifies the existence of a CameraUser relationship.
    """
    link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == user_id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=403, detail="Not authorized")
