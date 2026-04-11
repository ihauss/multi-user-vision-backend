from fastapi import APIRouter, Depends
from sqlmodel import Session
from fastapi import Request, HTTPException

from app.database import get_session
from app.services.camera_service import create_camera, add_user_to_camera, remove_user_from_camera, delete_camera
from app.services.frame_service import push_frame, get_last_frame
from app.schemas.camera import CameraResponse, AddUserRequest
from app.models import User
from app.core.dependencies import get_current_user, get_frame_repository


router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.post("/", response_model=CameraResponse)
def create_camera_route(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
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
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")

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
    return get_last_frame(
        session=session,
        camera_id=camera_id,
        current_user=current_user,
        repo=repo
    )
