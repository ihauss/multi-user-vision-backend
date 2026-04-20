from sqlmodel import Session, select
from fastapi import HTTPException
from app.models import Event, Camera, CameraUser
from app.services.utils import verify_api_key


def create_event(session: Session, api_key: str, data: dict):
    """
    Create a new event associated with a camera.

    Args:
        session (Session): Database session.
        api_key (str): Raw API key used to authenticate the camera/device.
        data (dict): Event payload containing:
            - camera_id (int): ID of the camera
            - type (str): Type of event (e.g., "motion", "alert")
            - description (str, optional): Human-readable description
            - importance (int, optional): Priority level (default = 1)
            - payload (dict, optional): Additional structured data

    Returns:
        dict:
            - id: ID of the created event

    Raises:
        HTTPException:
            - 404 if the camera does not exist
            - 401 if the API key is invalid

    Workflow:
        1. Retrieve the camera using the provided camera_id.
        2. Verify the API key against the stored hash.
        3. Create and persist the event.

    Notes:
        - Authentication is device-based (API key).
        - The payload structure is flexible but should ideally be validated upstream.
    """
    # Retrieve camera from database
    cam = session.get(Camera, data["camera_id"])

    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Verify API key matches the camera
    if not verify_api_key(api_key, cam.api_key_hash):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Create event object
    event = Event(
        camera_id=cam.id,
        type=data["type"],
        description=data.get("description"),
        importance=data.get("importance", 1),
        payload=data.get("payload"),
    )

    # Persist event
    session.add(event)
    session.commit()
    session.refresh(event)

    return {"id": event.id}


def get_events(session: Session, camera_id: int, current_user):
    """
    Retrieve all events associated with a given camera.

    Args:
        session (Session): Database session.
        camera_id (int): ID of the camera.
        current_user (User): Authenticated user requesting access.

    Returns:
        list[Event]: List of events for the camera.

    Raises:
        HTTPException:
            - 404 if camera does not exist
            - 403 if user does not have access

    Workflow:
        1. Verify that the camera exists.
        2. Check if the user is linked to the camera.
        3. Retrieve all associated events.

    Notes:
        - Access is granted to both owners and viewers.
        - No pagination is implemented (may become an issue with large datasets).
    """
    # Check if camera exists
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Verify access rights
    link = session.exec(
        select(CameraUser).where(
            CameraUser.camera_id == camera_id,
            CameraUser.user_id == current_user.id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Retrieve all events for the camera
    events = session.exec(
        select(Event).where(Event.camera_id == camera_id)
    ).all()

    return events
