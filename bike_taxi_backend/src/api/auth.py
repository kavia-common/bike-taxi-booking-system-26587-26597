from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import hmac
import base64
import json

from src.api.config import settings
from src.api.models import USERS, User, Role


security = HTTPBearer(auto_error=False)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(raw: str) -> str:
    # Simple salted SHA256 hashing; replace with bcrypt/argon2 in production
    salt = "biketaxi-salt"
    return hashlib.sha256((salt + raw).encode("utf-8")).hexdigest()


def verify_password(raw: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(raw), hashed)


def _jwt_sign(header: dict, payload: dict, secret: str) -> str:
    header_b = _b64url(json.dumps(header, separators=(',', ':')).encode())
    payload_b = _b64url(json.dumps(payload, separators=(',', ':')).encode())
    signing_input = f"{header_b}.{payload_b}".encode()
    sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    return f"{header_b}.{payload_b}.{_b64url(sig)}"


def _jwt_decode(token: str, secret: str) -> Tuple[dict, dict]:
    try:
        header_b, payload_b, sig_b = token.split(".")
        signing_input = f"{header_b}.{payload_b}".encode()
        expected_sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
        provided_sig = _b64url_decode(sig_b)
        if not hmac.compare_digest(expected_sig, provided_sig):
            raise ValueError("Invalid signature")
        header = json.loads(_b64url_decode(header_b))
        payload = json.loads(_b64url_decode(payload_b))
        return header, payload
    except Exception as e:
        raise ValueError("Invalid token") from e


# PUBLIC_INTERFACE
def create_access_token(user: User) -> Tuple[str, int]:
    """Create a signed JWT access token for a user."""
    exp_minutes = settings.access_token_exp_minutes
    now = datetime.utcnow()
    exp = now + timedelta(minutes=exp_minutes)
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role.value,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "iss": settings.app_name,
        "ver": settings.api_version,
    }
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    token = _jwt_sign(header, payload, settings.jwt_secret_key or "dev-secret")
    return token, int(exp_minutes * 60)


# PUBLIC_INTERFACE
def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """FastAPI dependency to extract current user from Authorization header."""
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    scheme = credentials.scheme.lower()
    if scheme != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")
    token = credentials.credentials
    try:
        _, payload = _jwt_decode(token, settings.jwt_secret_key or "dev-secret")
        user_id = payload.get("sub")
        if not user_id or user_id not in USERS:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        return USERS[user_id]
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


# PUBLIC_INTERFACE
def require_role(required: Role):
    """Dependency factory enforcing a specific user role."""
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role != required:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency
