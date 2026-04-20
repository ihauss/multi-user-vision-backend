import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_session


from app.models import user  


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False}
    )

    SQLModel.metadata.drop_all(engine)   # 🔥 ajout
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_repo():
    from app.core.dependencies import get_frame_repository
    repo = get_frame_repository()
    if hasattr(repo, "storage"):
        repo.storage.clear()
