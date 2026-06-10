import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import api.models  # noqa: F401  (registers tables on Base.metadata)
from api.dependencies.database import get_db
from api.main import create_app
from database.base import Base


@pytest.fixture()
def anon_client():
    """App wired to a fresh in-memory SQLite database, no user logged in."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        session = TestingSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


def register_user(client: TestClient, email: str = "test@example.com") -> str:
    """Register an account and return its bearer token."""
    response = client.post(
        "/api/v1/auth/register", json={"email": email, "password": "a-secure-pw"}
    )
    assert response.status_code == 201, response.text
    return response.json()["token"]


@pytest.fixture()
def client(anon_client):
    """Client authenticated as a freshly registered user (who therefore has
    the default category set)."""
    token = register_user(anon_client)
    anon_client.headers["Authorization"] = f"Bearer {token}"
    return anon_client
