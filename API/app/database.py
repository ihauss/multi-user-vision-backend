from sqlmodel import SQLModel, create_engine, Session

# Database connection URL.
# Uses SQLite for local development with a file-based database.
DATABASE_URL = "sqlite:///./app.db"

# Create the SQLAlchemy engine.
# The engine manages the database connection pool.
# `echo=True` enables SQL query logging (useful for debugging).
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """
    Provide a database session for request handling.

    Yields:
        Session: SQLModel database session.

    Behavior:
        - A new session is created for each request.
        - The session is automatically closed after use.

    Notes:
        - This function is designed to be used with FastAPI's dependency injection.
        - Ensures proper resource management (no session leaks).
    """
    with Session(engine) as session:
        yield session
