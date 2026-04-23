from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema representing an authentication token.

    Attributes:
        access_token (str): JWT access token used for authentication.
        token_type (str): Type of token (default is "bearer").

    Notes:
        - Returned after login or user creation.
        - Must be included in the Authorization header:
            Authorization: Bearer <token>
    """
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    """
    Schema used to create a new user.

    Attributes:
        username (str): Unique username.
        password (str): Raw password (will be hashed before storage).

    Notes:
        - Password is never stored in plaintext.
        - Validation should be added for security (length, complexity).
    """
    username: str
    password: str


class UserLogin(BaseModel):
    """
    Schema used for user authentication.

    Attributes:
        username (str): Username of the user.
        password (str): Raw password to verify.

    Notes:
        - Used to authenticate and generate a JWT token.
    """
    username: str
    password: str


class UserRead(BaseModel):
    """
    Public schema representing a user.

    Attributes:
        id (int): Unique user ID.
        username (str): Username of the user.

    Notes:
        - Safe to expose (no sensitive data).
    """
    id: int
    username: str
