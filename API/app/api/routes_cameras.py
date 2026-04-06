from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services.camera_service import create_camera
from app.schemas.camera import CameraResponse
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
