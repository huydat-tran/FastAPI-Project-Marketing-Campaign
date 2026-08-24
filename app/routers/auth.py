from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth import (
    authenticate_user,
    create_token_response,
    refresh_access_token,
    register_user,
)
from app.utils.exceptions import AppException
from app.utils.rate_limit import (
    check_login_rate_limit,
    record_login_attempt,
    reset_login_attempts,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):  # noqa: B008
    user = register_user(db, data)

    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):  # noqa: B008
    client_ip = request.client.host if request.client else "unknown"

    rate_key = f"login:{client_ip}"

    if not check_login_rate_limit(
        key=rate_key,
        max_attempts=settings.LOGIN_RATE_LIMIT,
        window_seconds=settings.LOGIN_RATE_WINDOW_SECONDS,
    ):
        raise AppException(
            status_code=429, message="Too many login attempts. Please try again later."
        )

    try:
        user = authenticate_user(db, data)

    except AppException:
        record_login_attempt(rate_key)
        raise

    reset_login_attempts(rate_key)

    return create_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),  # noqa: B008
):
    return refresh_access_token(db, data)
