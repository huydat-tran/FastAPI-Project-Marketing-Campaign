import jwt
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest
from app.services.user import get_user_by_email, get_user_by_id
from app.utils.exceptions import AppException


def register_user(db: Session, data: RegisterRequest) -> User:
    existing_user = get_user_by_email(db, data.email)

    if existing_user:
        raise AppException(status_code=400, message="Email is already registered")

    payload = data.model_dump()

    payload["password"] = hash_password(payload["password"])

    new_user = User(**payload)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def authenticate_user(db: Session, data: LoginRequest) -> User:
    user = get_user_by_email(db, data.email)

    if user is None:
        raise AppException(status_code=401, message="Invalid email or password")

    if not verify_password(data.password, user.password):
        raise AppException(status_code=401, message="Invalid email or password")

    if not user.is_active:
        raise AppException(status_code=401, message="Account is inactive")

    return user


def create_token_response(user: User) -> dict:
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }


def refresh_access_token(
    db: Session,
    data: RefreshTokenRequest,
) -> dict:
    try:
        payload = decode_token(data.refresh_token)

    except jwt.ExpiredSignatureError:
        raise AppException(
            status_code=401,
            message="Refresh token has expired",
        )

    except jwt.PyJWTError:
        raise AppException(
            status_code=401,
            message="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise AppException(
            status_code=401,
            message="Invalid refresh token",
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise AppException(
            status_code=401,
            message="Invalid refresh token",
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise AppException(
            status_code=401,
            message="Invalid refresh token",
        )

    user = get_user_by_id(db, user_id)

    if user is None:
        raise AppException(
            status_code=401,
            message="User not found",
        )

    if not user.is_active:
        raise AppException(
            status_code=403,
            message="Account is inactive",
        )

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": data.refresh_token,
        "token_type": "bearer",
    }
