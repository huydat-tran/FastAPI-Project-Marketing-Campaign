from sqlalchemy.orm import Session

from app.models.task_comment import TaskComment
from app.models.user import User
from app.schemas.task_comment import TaskCommentCreate
from app.services.campaign import require_campaign_member
from app.services.campaign_task import get_task_by_id
from app.utils.exceptions import AppException


def create_task_comment(
    db: Session, task_id: int, data: TaskCommentCreate, current_user: User
) -> TaskComment:
    task = get_task_by_id(db, task_id)

    if task is None:
        raise AppException(status_code=404, message="Campaign task not found")

    require_campaign_member(db, task.campaign_id, current_user.id)

    content = data.content.strip()

    if not content:
        raise AppException(status_code=400, message="Content cannot be empty")

    comment = TaskComment(task_id=task_id, user_id=current_user.id, content=content)

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_task_comments(
    db: Session, task_id: int, current_user: User
) -> list[TaskComment]:
    task = get_task_by_id(db, task_id)

    if task is None:
        raise AppException(status_code=404, message="Campaign task not found")

    require_campaign_member(db, task.campaign_id, current_user.id)

    return (
        db.query(TaskComment)
        .filter(
            TaskComment.task_id == task_id,
        )
        .order_by(TaskComment.created_at.asc())
        .all()
    )
