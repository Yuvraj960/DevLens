from app.models import File
from app.services.discovery.auth_extractor import AuthExtractor


def test_auth_extractor():
    files = [
        File(path="app/core/security.py", language="python", size_bytes=100, loc=20, content_hash="ha1"),
        File(path="app/api/v1/jwt_auth.py", language="python", size_bytes=150, loc=30, content_hash="ha2"),
    ]

    auth_flow = AuthExtractor.extract_auth_flow(files)

    assert "steps" in auth_flow
    assert "token_handling" in auth_flow
    assert auth_flow["token_handling"]["type"] == "jwt"
    assert len(auth_flow["steps"]) >= 4
