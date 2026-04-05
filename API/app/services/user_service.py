from sqlmodel import Session, select
from app.models.user import User
from app.core.security import hash_password, verify_password


class UserService:
    def create_user(self, session: Session, username: str, password: str):
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
        user = session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        session.delete(user)
        session.commit()

    def authenticate(self, session: Session, username: str, password: str):
        user = session.exec(
            select(User).where(User.username == username)
        ).first()

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user
