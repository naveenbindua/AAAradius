from fastapi.testclient import TestClient

from aaaradius.db import init_db, seed_demo_data
from aaaradius.main import app


def setup_module() -> None:
    init_db()
    seed_demo_data()


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_success() -> None:
    response = client.post(
        "/api/auth",
        json={"username": "demo", "password": "radius123", "nas_name": "office-wifi"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["packet"] == "Access-Accept"


def test_auth_reject_bad_password() -> None:
    response = client.post(
        "/api/auth",
        json={"username": "demo", "password": "wrong", "nas_name": "office-wifi"},
    )
    body = response.json()
    assert body["success"] is False
    assert body["packet"] == "Access-Reject"


def test_create_user_via_form() -> None:
    username = "alice-e2e"
    response = client.post(
        "/users",
        data={"username": username, "password": "secret"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    page = client.get("/users")
    assert username in page.text
