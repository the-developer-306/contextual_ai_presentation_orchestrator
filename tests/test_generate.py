def test_generate_presentation(client, auth_headers):
    response = client.post("/api/generate-presentation?topic=AI", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "ppt_json" in data
    assert "slides" in data["ppt_json"]
