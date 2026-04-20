from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """
    Database model representing an application user.

    Attributes:
        id (Optional[int]): Primary key of the user.
        username (str): Unique username used for authentication.
        password_hash (str): Hashed password (never stored in plaintext).
        created_at (datetime): Timestamp of user creation.

    Notes:
        - Passwords are securely hashed using bcrypt (see security module).
        - Username is indexed and must be unique.
        - This model is used for authentication and access control.
    """

    # Unique identifier for the user
    id: Optional[int] = Field(default=None, primary_key=True)

    # Username used for login
    # Indexed for faster lookup and enforced as unique
    username: str = Field(index=True, unique=True)

    # Hashed password (never store raw passwords)
    password_hash: str

    # Timestamp of account creation
    created_at: datetime = Field(default_factory=datetime.utcnow)
