from fastapi import APIRouter, HTTPException, status
from typing import List

from src.api.schemas import UserCreate, UserLogin, UserOut, Token
from src.api.models import USERS, User, Role
from src.api.models import gen_id
from src.api.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"], responses={404: {"description": "Not found"}})


@router.post("/register", summary="Register user", response_model=UserOut, status_code=201)
def register_user(body: UserCreate):
    """Register a new user with email, password, name and role.

    Parameters:
        body: UserCreate - registration details.
    Returns:
        UserOut: created user data without sensitive fields.
    """
    # ensure email uniqueness
    if any(u.email.lower() == body.email.lower() for u in USERS.values()):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        id=gen_id(),
        email=body.email.lower(),
        name=body.name,
        role=Role(body.role.value),
        hashed_password=hash_password(body.password),
    )
    USERS[user.id] = user
    return UserOut(id=user.id, email=user.email, name=user.name, role=user.role.value, created_at=user.created_at)


@router.post("/login", summary="User login", response_model=Token)
def login(body: UserLogin):
    """Authenticate a user and returns a bearer token.

    Parameters:
        body: UserLogin - email and password.
    Returns:
        Token: JWT access token.
    """
    user = next((u for u in USERS.values() if u.email == body.email.lower()), None)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token, expires_in = create_access_token(user)
    return Token(access_token=token, expires_in=expires_in)


@router.get("/users", summary="List users", response_model=List[UserOut])
def list_users():
    """List all users (demo endpoint, not secured)."""
    return [UserOut(id=u.id, email=u.email, name=u.name, role=u.role.value, created_at=u.created_at) for u in USERS.values()]
