from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.task_attachment import TaskAttachmentResponse
from app.services.task_attachment import create_task_attachment, get_task_attachment

router = APIRouter(
    tags=["Task Attachments"],
)


@router.post(
    "/campaign-tasks/{task_id}/attachments",
    response_model=TaskAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return create_task_attachment(db, task_id, file, current_user)


@router.get(
    "/campaign-tasks/attachments/{attachment_id}",
    response_model=TaskAttachmentResponse,
)
def get_attachment_detail(
    attachment_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_task_attachment(db, attachment_id, current_user)
