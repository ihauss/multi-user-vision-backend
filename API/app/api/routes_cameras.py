from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services.camera_service import create_camera, add_user_to_camera
from app.schemas.camera import CameraResponse, AddUserRequest
from app.models import User
from app.core.dependencies import get_current_user

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
