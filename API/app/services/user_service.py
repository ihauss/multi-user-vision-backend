from sqlmodel import Session, select
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


class UserService:
    """
    Service layer responsible for user management and authentication.

    This class encapsulates all business logic related to:
        - User creation
        - User deletion
        - Authentication
        - Token generation

    Notes:
        - Database access is handled via SQLModel sessions.
        - Security-sensitive operations (hashing, token creation) are delegated
          to the security module.
    """

    def create_user(self, session: Session, username: str, password: str):
        """
        Create a new user.

        Args:
            session (Session): Database session.
            username (str): Desired username.
            password (str): Raw password.

        Returns:
            User: The created user object.

        Raises:
            ValueError: If the username already exists.

        Workflow:
            1. Check if the username is already taken.
            2. Hash the password securely.
            3. Create and persist the user in the database.

        Notes:
            - Passwords are never stored in plaintext.
            - Uniqueness is enforced at the application level here (should also exist at DB level).
        """
        existing = session.exec(
            select(User).where(User.username == username)
        ).first()

        if existing:
            raise ValueError("Username already exists")

        user = User(
            username=username,
            password_hash=hash_password(password)
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def delete_user(self, session: Session, user_id: int):
        """
        Delete a user by ID.

        Args:
            session (Session): Database session.
            user_id (int): ID of the user to delete.

        Raises:
            ValueError: If the user does not exist.

        Notes:
            - This operation is irreversible.
            - Associated resources should ideally be handled (cascade or cleanup).
        """
        user = session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        session.delete(user)
        session.commit()

    def authenticate(self, session: Session, username: str, password: str):
        """
        Authenticate a user using username and password.

        Args:
            session (Session): Database session.
            username (str): Username.
            password (str): Raw password.

        Returns:
            User or None:
                - User object if authentication succeeds
                - None if authentication fails

        Workflow:
            1. Retrieve user by username.
            2. Verify the provided password against the stored hash.

        Notes:
            - Returns None instead of raising to avoid leaking information.
            - Password verification is handled securely via hashing.
        """
        user = session.exec(
            select(User).where(User.username == username)
        ).first()

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user


    def create_user_with_token(self, session: Session, username: str, password: str):
        """
        Create a new user and immediately generate an access token.

        Args:
            session (Session): Database session.
            username (str): Desired username.
            password (str): Raw password.

        Returns:
            tuple:
                - User: Created user
                - str: Access token

        Notes:
            - This is typically used during user registration.
            - Token payload includes the user ID as subject ("sub").
        """
        user = self.create_user(session, username, password)
        token = create_access_token({"sub": str(user.id)})

        return user, token


    def login_with_token(self, session: Session, username: str, password: str):
        """
        Authenticate a user and return an access token.

        Args:
            session (Session): Database session.
            username (str): Username.
            password (str): Raw password.

        Returns:
            str or None:
                - Access token if authentication succeeds
                - None if authentication fails

        Workflow:
            1. Authenticate user credentials.
            2. Generate a token if authentication succeeds.

        Notes:
            - Token payload includes the user ID as subject ("sub").
            - No distinction is made between invalid username or password.
        """
        user = self.authenticate(session, username, password)

        if not user:
            return None

        token = create_access_token({"sub": str(user.id)})

        return token
