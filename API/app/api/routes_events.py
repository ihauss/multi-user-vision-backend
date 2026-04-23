from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from app.database import get_session
from app.services.events import create_event, get_events
from app.core.dependencies import get_current_user

# Initialize a router dedicated to event-related endpoints.
# All routes in this file will be prefixed with "/events".
router = APIRouter(prefix="/events", tags=["events"])


@router.post("")
def create_event_route(
    request: Request,
    payload: dict,
    session: Session = Depends(get_session),
):
    """
    Create a new event associated with a camera or system component.

    This endpoint is typically used by external services or devices
    (e.g., vision models, cameras) to push detected events.

    Args:
        request (Request): Incoming HTTP request used to extract headers.
        payload (dict): Raw event data sent by the client.
        session (Session): Database session.

    Returns:
        Result of the event creation process.

    Raises:
        HTTPException:
            - 401 if the API key is missing or invalid.

    Notes:
        - Authentication is performed using a Bearer API key.
        - The payload structure is not validated at this level and is passed directly
          to the service layer.
        - The service layer is responsible for validating and storing the event.
    """
    auth = request.headers.get("Authorization")

    # Validate Authorization header format
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")

    # Extract API key from the Authorization header
    api_key = auth.split(" ")[1]

    # Delegate event creation to the service layer
    return create_event(session=session, api_key=api_key, data=payload)
