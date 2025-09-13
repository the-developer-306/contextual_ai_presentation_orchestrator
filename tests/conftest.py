import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def auth_headers(client):
    login = client.post("/api/login", json={"email": "exec@example.com", "password": "password"})
    token = login.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}
