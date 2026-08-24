from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.role import RequireRole
from app.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.services.user import get_users

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):  # noqa: B008
    return current_user


@router.get("", response_model=list[UserResponse])
def list_users(
    search: str | None = Query(default=None, description="Search by full name"),
    is_active: bool | None = Query(
        default=None, description="Filter by account status"
    ),
    current_user: User = Depends(RequireRole(UserRole.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_users(
        db,
        search,
        is_active,
    )
