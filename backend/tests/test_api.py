import pytest
from app import create_app, db


@pytest.fixture
def client():
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def register(client, email="vol@test.com", role="volunteer"):
    resp = client.post("/api/auth/register", json={
        "email": email, "password": "pass123", "role": role
    })
    return resp.get_json()["token"]


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_register_and_login(client):
    token = register(client)
    assert token is not None

    resp = client.post("/api/auth/login", json={"email": "vol@test.com", "password": "pass123"})
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_register_duplicate_email_fails(client):
    register(client, email="dup@test.com")
    resp = client.post("/api/auth/register", json={
        "email": "dup@test.com", "password": "pass123", "role": "volunteer"
    })
    assert resp.status_code == 409


def test_create_and_list_submission(client):
    token = register(client, email="vol2@test.com")
    resp = client.post("/api/submissions",
        headers={"Authorization": f"Bearer {token}"},
        json={"photo_url": "https://example.com/x.jpg", "latitude": 1.0, "longitude": 2.0})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "pending"
    assert data["ai_category"] is not None  # AI tagger stub ran

    resp = client.get("/api/submissions", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_submission_requires_photo_url(client):
    token = register(client, email="vol3@test.com")
    resp = client.post("/api/submissions",
        headers={"Authorization": f"Bearer {token}"},
        json={"latitude": 1.0})
    assert resp.status_code == 400


def test_verification_requires_researcher_role(client):
    vol_token = register(client, email="vol4@test.com", role="volunteer")
    resp = client.post("/api/submissions",
        headers={"Authorization": f"Bearer {vol_token}"},
        json={"photo_url": "https://example.com/x.jpg"})
    sub_id = resp.get_json()["id"]

    # Volunteer tries to verify -> should be forbidden
    resp = client.post(f"/api/verifications/{sub_id}",
        headers={"Authorization": f"Bearer {vol_token}"},
        json={"decision": "verified"})
    assert resp.status_code == 403


def test_researcher_can_verify_submission(client):
    vol_token = register(client, email="vol5@test.com", role="volunteer")
    res_token = register(client, email="res5@test.com", role="researcher")

    resp = client.post("/api/submissions",
        headers={"Authorization": f"Bearer {vol_token}"},
        json={"photo_url": "https://example.com/x.jpg"})
    sub_id = resp.get_json()["id"]

    resp = client.post(f"/api/verifications/{sub_id}",
        headers={"Authorization": f"Bearer {res_token}"},
        json={"decision": "verified", "comment": "confirmed"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "verified"
