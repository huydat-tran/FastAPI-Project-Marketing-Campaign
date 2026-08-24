import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.database import get_db
from app.models.user import User
from app.services.user import get_user_by_id
from app.utils.exceptions import AppException

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> User:
    token = credentials.credentials

    try:
        payload = decode_token(token)

    except jwt.ExpiredSignatureError:
        raise AppException(
            status_code=401,
            message="Token has expired",
        )

    except jwt.PyJWTError:
        raise AppException(
            status_code=401,
            message="Invalid Token",
        )

    if payload.get("type") != "access":
        raise AppException(status_code=401, message="Invalid access token")

    user_id = payload.get("sub")

    if user_id is None:
        raise AppException(status_code=401, message="Invalid Token")

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        raise AppException(status_code=401, message="Invalid Token")

    user = get_user_by_id(db, user_id)

    if user is None:
        raise AppException(status_code=404, message="User not found")

    if not user.is_active:
        raise AppException(status_code=403, message="Account is inactive")

    return user
