def test_login_success(client):
    response = client.post("/api/login", json={"email": "exec@example.com", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "Executive"

def test_login_failure(client):
    response = client.post("/api/login", json={"email": "fake@example.com", "password": "wrong"})
    assert response.status_code == 401
