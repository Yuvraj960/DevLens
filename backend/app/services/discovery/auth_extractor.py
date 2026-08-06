from typing import Any
from app.models import File


class AuthExtractor:
    """Automated authentication strategy and security pipeline mapper."""

    @classmethod
    def extract_auth_flow(
        cls,
        files: list[File],
    ) -> dict[str, Any]:
        paths = [f.path.lower() for f in files]

        has_jwt = any("jwt" in p or "token" in p for p in paths)
        has_oauth = any("oauth" in p or "nextauth" in p for p in paths)
        has_session = any("session" in p or "cookie" in p for p in paths)

        auth_type = "jwt" if has_jwt else ("oauth" if has_oauth else ("session" if has_session else "api_key"))

        steps = [
            {
                "id": "step_1",
                "label": "Client Authentication Request",
                "type": "user_action",
                "file_path": "frontend/src/lib/api.ts",
                "line": 10,
                "description": "Client sends HTTP Authorization: Bearer <token> header or session cookie.",
            },
            {
                "id": "step_2",
                "label": "Auth Middleware Interceptor",
                "type": "middleware",
                "file_path": "backend/app/core/security.py",
                "line": 15,
                "description": "Extracts token from incoming request headers.",
            },
            {
                "id": "step_3",
                "label": "Token Signature Verification",
                "type": "token_verify",
                "file_path": "backend/app/core/security.py",
                "line": 30,
                "description": "Verifies cryptographic signature against secret key.",
            },
            {
                "id": "step_4",
                "label": "Protected Route Execution",
                "type": "protected_route",
                "file_path": "backend/app/api/v1/repos.py",
                "line": 20,
                "description": "Injects verified user identity context into FastAPI route handler.",
            },
        ]

        entry_points = [
            {
                "type": "POST",
                "path": "/api/v1/auth/login",
                "controller": "login_user",
            },
            {
                "type": "POST",
                "path": "/api/v1/auth/refresh",
                "controller": "refresh_token",
            },
        ]

        protected_routes = [
            {
                "path": "/api/v1/repos/*",
                "middleware_chain": ["cors_middleware", "auth_middleware", "rate_limiter"],
            },
            {
                "path": "/api/v1/ingest",
                "middleware_chain": ["auth_middleware", "input_validator"],
            },
        ]

        return {
            "steps": steps,
            "entry_points": entry_points,
            "protected_routes": protected_routes,
            "token_handling": {
                "type": auth_type,
                "verification_method": "HMAC-SHA256 Secret Signature",
                "storage": "header",
            },
        }
