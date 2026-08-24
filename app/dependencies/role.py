from fastapi import Depends

from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.utils.exceptions import AppException


class RequireRole:
    def __init__(self, *allowed_roles: UserRole):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:  # noqa: B008
        if current_user.role not in self.allowed_roles:
            raise AppException(
                status_code=403,
                message="You don't have permission to access this resource",
            )

        return current_user
