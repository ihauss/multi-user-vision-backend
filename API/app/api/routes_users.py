from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

service = UserService()


@router.post("/", response_model=UserRead)
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    try:
        user = service.create_user(session, data.username, data.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    try:
        service.delete_user(session, user_id)
        return {"message": "User deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/login", response_model=UserRead)
def login(data: UserLogin, session: Session = Depends(get_session)):
    user = service.authenticate(session, data.username, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user
