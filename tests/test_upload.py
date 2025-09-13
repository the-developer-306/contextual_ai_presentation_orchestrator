def test_upload_small_txt(client, auth_headers, tmp_path):
    # Create a dummy txt file
    file_path = tmp_path / "test.txt"
    file_path.write_text("AI is transforming industries.")

    with open(file_path, "rb") as f:
        response = client.post("/api/upload-doc", files={"files": ("test.txt", f, "text/plain")}, headers=auth_headers)

    assert response.status_code == 200
    assert "message" in response.json() or "success" in response.json()
