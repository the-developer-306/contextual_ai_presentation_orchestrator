def test_download_ppt(client, auth_headers):
    fake_json = {
        "slides": [{"title": "Intro", "content": [{"statement": "AI is shaping the future"}]}],
        "summary": "AI overview"
    }

    response = client.post("/api/download-ppt", json=fake_json, headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment")
    assert response.content  # should contain pptx bytes
def test_download_ppt(client, auth_headers):
    fake_json = {
        "slides": [{"title": "Intro", "content": [{"statement": "AI is shaping the future"}]}],
        "summary": "AI overview"
    }

    response = client.post("/api/download-ppt", json=fake_json, headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment")
    assert response.content  # should contain pptx bytes
