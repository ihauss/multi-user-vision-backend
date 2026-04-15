from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.user_service import UserService
from app.schemas.user import Token
from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/users", tags=["users"])

service = UserService()


@router.post("/", response_model=Token)
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    try:
        user, token = service.create_user_with_token(
            session, data.username, data.password
        )
        return {"access_token": token}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.delete("/me")
def delete_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    service.delete_user(session, current_user.id)
    return {"message": "User deleted"}


@router.post("/login", response_model=Token)
def login(data: UserLogin, session: Session = Depends(get_session)):
    token = service.login_with_token(session, data.username, data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": token}
