from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.task_comment import (
    TaskCommentCreate,
    TaskCommentResponse,
)
from app.services.task_comment import (
    create_task_comment,
    get_task_comments,
)

router = APIRouter(tags=["Task Comments"])


@router.post(
    "/campaign-tasks/{task_id}/comments",
    response_model=TaskCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    task_id: int,
    data: TaskCommentCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return create_task_comment(db, task_id, data, current_user)


@router.get(
    "/campaign-tasks/{task_id}/comments",
    response_model=list[TaskCommentResponse],
)
def list_comments(
    task_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_task_comments(
        db,
        task_id,
        current_user,
    )
