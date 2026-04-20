from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.user_service import UserService
from app.schemas.user import Token
from app.core.dependencies import get_current_user
from app.models.user import User


# Initialize a router dedicated to user-related endpoints.
# All routes in this file will be prefixed with "/users".
router = APIRouter(prefix="/users", tags=["users"])

# Instantiate the user service which contains business logic
# related to user management (creation, authentication, deletion).
service = UserService()


@router.post("/", response_model=Token)
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    """
    Create a new user and return an authentication token.

    Args:
        data (UserCreate): Payload containing user credentials (username, password).
        session (Session): Database session injected via dependency.

    Returns:
        Token:
            - access_token: JWT or similar token used for authentication.

    Raises:
        HTTPException:
            - 400 if user creation fails (e.g., username already exists).

    Notes:
        - The password is expected to be handled securely (e.g., hashed in service layer).
        - A token is immediately generated after successful registration.
    """
    try:
        user, token = service.create_user_with_token(
            session, data.username, data.password
        )
        return {"access_token": token}
    except ValueError as e:
        # Convert service-level validation errors into HTTP 400 responses
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's information.

    Args:
        current_user (User): User extracted from the authentication token.

    Returns:
        UserRead: Public representation of the user.

    Notes:
        - This endpoint relies entirely on authentication middleware/dependency.
        - No database query is needed if the user is already loaded in the dependency.
    """
    return current_user


@router.delete("/me")
def delete_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete the currently authenticated user.

    Args:
        current_user (User): Authenticated user.
        session (Session): Database session.

    Returns:
        dict: Confirmation message.

    Notes:
        - This operation is irreversible.
        - Associated resources (if any) should be handled in the service layer.
    """
    service.delete_user(session, current_user.id)
    return {"message": "User deleted"}


@router.post("/login", response_model=Token)
def login(data: UserLogin, session: Session = Depends(get_session)):
    """
    Authenticate a user and return an access token.

    Args:
        data (UserLogin): Payload containing username and password.
        session (Session): Database session.

    Returns:
        Token:
            - access_token: Authentication token if credentials are valid.

    Raises:
        HTTPException:
            - 401 if authentication fails.

    Notes:
        - Authentication logic (password verification, hashing, etc.) is handled in the service layer.
        - No information is leaked about which part of the credentials is incorrect.
    """
    token = service.login_with_token(session, data.username, data.password)

    # If authentication fails, return a generic unauthorized error
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": token}
