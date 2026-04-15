from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from app.database import get_session
from app.services.events import create_event, get_events
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/events", tags=["events"])


@router.post("")
def create_event_route(
    request: Request,
    payload: dict,
    session: Session = Depends(get_session),
):
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")

    api_key = auth.split(" ")[1]

    return create_event(session=session, api_key=api_key, data=payload)
