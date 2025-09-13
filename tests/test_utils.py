from utils.security import create_access_token, verify_token
from utils.ppt_generator import PPTGenerator

def test_security_jwt():
    token = create_access_token({"sub": "test@example.com", "role": "Executive"})
    payload = verify_token(token)
    assert payload["role"] == "Executive"

def test_ppt_generator(tmp_path):
    ppt_gen = PPTGenerator(output_dir=str(tmp_path))
    fake_json = {
        "slides": [{"title": "Intro", "content": [{"statement": "AI is cool", "status": "ok", "design_hint": ""}]}],
        "summary": "test"
    }
    path = ppt_gen.generate_ppt(fake_json, filename="test.pptx")
    assert path.endswith(".pptx")
