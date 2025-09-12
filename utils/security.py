import os
import time
from typing import List, Optional
from jose import jwt, JWTError
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Config
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_now")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("JWT_EXP_SECONDS", 60 * 60 * 4))  # 4 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

# Demo users (replace with DB in prod)
DEMO_USERS = {
    "exec@example.com": {
        "name": "Exec User",
        "role": "Executive",
        "password_hash": pwd_context.hash("execpass")
    },
    "senior@example.com": {
        "name": "Senior User",
        "role": "Senior Manager",
        "password_hash": pwd_context.hash("seniorpass")
    },
    "analyst@example.com": {
        "name": "Analyst User",
        "role": "Analyst",
        "password_hash": pwd_context.hash("analystpass")
    },
    "junior@example.com": {
        "name": "Junior User",
        "role": "Junior Staff",
        "password_hash": pwd_context.hash("juniorpass")
    },
}


def create_access_token(subject: str, role: str, expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    """Create JWT with role embedded."""
    now = int(time.time())
    payload = {
        "sub": subject,
        "role": role.strip(),  # keep stored role clean
        "iat": now,
        "exp": now + expires_in,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    """Verify JWT and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate against DEMO_USERS store."""
    user = DEMO_USERS.get(email)
    if not user:
        return None
    if not pwd_context.verify(password, user["password_hash"]):
        return None
    return {"email": email, "name": user["name"], "role": user["role"]}


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer)) -> dict:
    """Extract user info from JWT credentials."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    token = credentials.credentials
    payload = verify_token(token)

    # Debug log
    print("🔑 Decoded JWT payload:", payload)

    return {"email": payload["sub"], "role": payload["role"]}


def require_role(allowed_roles: List[str]):
    """
    Dependency factory that raises 403 if current user's role
    not in allowed_roles. Role comparison is case-insensitive.
    """
    def dependency(user: dict = Depends(get_current_user)):
        user_role = user["role"].strip().lower()
        allowed_normalized = [r.strip().lower() for r in allowed_roles]

        # Debug log
        print("DEBUG ROLE CHECK:", user_role, "allowed:", allowed_normalized)

        if user_role not in allowed_normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for role {user['role']}"
            )
        return user

    return dependency
