import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from sqlmodel.pool import StaticPool

from app.dependencies import get_oidc_keycloak_user, get_session
from app.main import app
from app.models.keycloak import KeycloakIDToken


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_authorized")
def client_authorized_fixture(session: Session):
    def get_oidc_keycloak_user_override():
        return KeycloakIDToken(
            iss="https://lemur-15.cloud-iam.com/auth/realms/sentiment-analyzer",
            sub="3c40da3a-483a-4736-b7e1-a85069298bd7",
            aud=["account"],
            exp=1727143265,
            iat=1727107266,
            email="olya.shavochkina@yandex.ru",
            organization={"murmurmur": dict()},
        )

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_oidc_keycloak_user] = get_oidc_keycloak_user_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_read_main(client: TestClient):
    response = client.get("/")
    assert response.status_code == 404


protected_paths = [
    ("/api/v1/uploads", ["GET", "POST"]),
    ("/api/v1/uploads/1", ["GET", "DELETE"]),
    ("/api/v1/uploads/1/share", ["POST"]),
]


@pytest.mark.parametrize("path, actions", protected_paths)
def test_auth_required(client: TestClient, path: str, actions: list[str]):
    for action in actions:
        response = getattr(client, action.lower())(path)
        assert response.status_code == 403


def test_current_user(client_authorized: TestClient):
    response = client_authorized.get("/api/v1/users/me")
    assert response.status_code == 200
    assert response.json() == {
        "email": "olya.shavochkina@yandex.ru",
        "organization": "murmurmur",
        "id": "3c40da3a-483a-4736-b7e1-a85069298bd7",
    }


def test_uploads_empty(client_authorized: TestClient):
    response = client_authorized.get("/api/v1/uploads")
    assert response.status_code == 200
    assert response.json() == []


def test_text_check(client_authorized: TestClient):
    response = client_authorized.get(
        "/api/v1/check",
        params={"text": "I love FastAPI"},
    )
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data["results"][0]["text"] == "I love FastAPI"
    assert data["results"][0]["sentiment"] == "positive"


def test_create_upload(client_authorized: TestClient):
    response = client_authorized.post("/api/v1/uploads")
    files = {"file": ("test.txt", "I love your job", "text/plain")}
    response = client_authorized.post("/api/v1/uploads", files=files)
    assert response.status_code == 200
    data = response.json()
    upload_id = data["id"]
    assert isinstance(upload_id, int)

    created_at = data["created_at"]
    created_ad_dt = datetime.datetime.fromisoformat(created_at)
    assert (
        created_ad_dt < datetime.datetime.now()
        and created_ad_dt > datetime.datetime.now() - datetime.timedelta(seconds=10)
    )

    assert data["status"] == "pending"
    assert len(data["entries"]) == 1
    assert data["entries"][0]["text"] == "I love your job"
    assert data["format"] == "plain"

    response = client_authorized.get("/api/v1/uploads")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == upload_id
    assert data[0]["format"] == "plain"
