from fastapi import APIRouter, Depends
from sqlmodel import Session
from fastapi import Request, HTTPException
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

from app.database import get_session
from app.services.camera_service import create_camera, add_user_to_camera, remove_user_from_camera, delete_camera
from app.services.frame_service import push_frame, get_last_frame
from app.services.camera_service import check_camera_access
from app.services.events import get_events
from app.schemas.camera import CameraResponse, AddUserRequest
from app.models import User, Camera
from app.core.dependencies import get_current_user, get_frame_repository
from app.core.dependencies import get_user_from_token


# Initialize a router dedicated to camera-related endpoints.
# All routes in this file will be prefixed with "/cameras".
router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.post("/", response_model=CameraResponse)
def create_camera_route(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Create a new camera associated with the authenticated user.

    Args:
        session (Session): Database session injected via dependency.
        current_user (User): Authenticated user retrieved from the token.

    Returns:
        CameraResponse:
            - camera_id: Unique identifier of the created camera.
            - api_key: API key associated with the camera (used for pushing frames).

    Notes:
        - The API key is typically used by external devices (e.g., cameras) to authenticate.
        - This endpoint should only be accessible to authenticated users.
    """
    camera, api_key = create_camera(session, current_user.id)

    return CameraResponse(
        camera_id=camera.id,
        api_key=api_key
    )


@router.post("/{camera_id}/users")
def add_user(
    camera_id: int,
    data: AddUserRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Add a user to a camera's access list.

    Args:
        camera_id (int): ID of the camera.
        data (AddUserRequest): Payload containing the username to add.
        session (Session): Database session.
        current_user (User): Authenticated user performing the action.

    Returns:
        Result of the service layer operation.

    Notes:
        - The current user must have sufficient permissions (e.g., owner).
        - The target user is identified by username.
    """
    return add_user_to_camera(
        session=session,
        camera_id=camera_id,
        target_username=data.username,
        current_user=current_user,
    )


@router.delete("/{camera_id}/users/{username}")
def remove_user(
    camera_id: int,
    username: str,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Remove a user from a camera's access list.

    Args:
        camera_id (int): ID of the camera.
        username (str): Username of the user to remove.
        session (Session): Database session.
        current_user (User): Authenticated user performing the action.

    Returns:
        Result of the service layer operation.

    Notes:
        - Only authorized users (e.g., camera owner) should be allowed to perform this action.
    """
    return remove_user_from_camera(
        session=session,
        camera_id=camera_id,
        username=username,
        current_user=current_user
    )


@router.delete("/{camera_id}")
def delete_camera_route(
    camera_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Delete a camera.

    Args:
        camera_id (int): ID of the camera to delete.
        session (Session): Database session.
        current_user (User): Authenticated user.

    Returns:
        Result of the deletion operation.

    Notes:
        - Only the owner of the camera should be able to delete it.
        - This operation is irreversible.
    """
    return delete_camera(
        session=session,
        camera_id=camera_id,
        current_user=current_user
    )


@router.post("/frame")
def push_frame_route(
    request: Request,
    payload: dict,
    repo = Depends(get_frame_repository),
    session: Session = Depends(get_session)
):
    """
    Push a new frame to the system.

    This endpoint is typically called by external camera devices.

    Args:
        request (Request): Incoming HTTP request (used to extract headers).
        payload (dict): Request body containing frame data.
        repo: Frame repository (e.g., Redis) used for storage.
        session (Session): Database session.

    Returns:
        Result of the frame storage operation.

    Raises:
        HTTPException: If the API key is missing or invalid.

    Notes:
        - Authentication is done via a Bearer API key in the Authorization header.
        - The payload must contain a "data" field with the frame content.
    """
    auth = request.headers.get("Authorization")

    # Validate Authorization header format
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")

    # Extract API key from header
    api_key = auth.split(" ")[1]

    return push_frame(
        session=session,
        api_key=api_key,
        data=payload["data"],
        repo=repo
    )


@router.get("/{camera_id}/frame")
def get_frame(
    camera_id: int,
    session: Session = Depends(get_session),
    repo = Depends(get_frame_repository),
    current_user = Depends(get_current_user)
):
    """
    Retrieve the latest frame for a given camera.

    Args:
        camera_id (int): ID of the camera.
        session (Session): Database session.
        repo: Frame repository (e.g., Redis).
        current_user (User): Authenticated user.

    Returns:
        The latest frame data.

    Notes:
        - Access control is enforced to ensure the user can view this camera.
        - The frame is retrieved from a fast-access storage (e.g., Redis).
    """
    return get_last_frame(
        session=session,
        camera_id=camera_id,
        current_user=current_user,
        repo=repo
    )


@router.websocket("/ws/{camera_id}")
async def websocket_camera_stream(
    websocket: WebSocket,
    camera_id: int,
    repo = Depends(get_frame_repository),
    session: Session = Depends(get_session),
):
    """
    WebSocket endpoint to stream live frames from a camera.

    Args:
        websocket (WebSocket): WebSocket connection instance.
        camera_id (int): ID of the camera to stream.
        repo: Frame repository (e.g., Redis).
        session (Session): Database session.

    Behavior:
        - Authenticates the user using a token passed as a query parameter.
        - Verifies access rights to the camera.
        - Continuously polls for new frames and sends them to the client.

    Notes:
        - Uses polling (every 100ms) to check for new frames.
        - Sends frames only if they have changed since the last iteration.
        - Closes connection on authentication failure.
    """
    token = websocket.query_params.get("token")

    # Reject connection if no token is provided
    if not token:
        await websocket.close(code=1008)
        return

    try:
        # Authenticate user from token
        current_user = get_user_from_token(token, session)

        # Check if camera exists
        camera = session.get(Camera, camera_id)
        if not camera:
            await websocket.close(code=1008)
            return

        # Verify user has access to this camera
        check_camera_access(session, camera_id, current_user.id)

    except Exception as e:
        # Close connection if authentication or authorization fails
        await websocket.close(code=1008)
        return

    await websocket.accept()

    last_frame = None

    try:
        while True:
            # Retrieve latest frame from repository
            frame = repo.get(camera_id)

            # Send only if new frame is available
            if frame and frame != last_frame:
                await websocket.send_json({"data": frame})
                last_frame = frame

            # Prevent tight loop (reduces CPU usage)
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        # Gracefully handle client disconnection
        pass


@router.get("/{camera_id}/events")
def get_camera_events(
    camera_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user),
):
    """
    Retrieve events associated with a camera.

    Args:
        camera_id (int): ID of the camera.
        session (Session): Database session.
        current_user (User): Authenticated user.

    Returns:
        List of events related to the camera.

    Notes:
        - Access control is enforced.
        - Events may include detections, alerts, or system logs.
    """
    return get_events(
        session=session,
        camera_id=camera_id,
        current_user=current_user
    )
