import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.services.campaign_task import get_task_by_id
from app.models.task_attachment import TaskAttachment
from app.models.user import User
from app.services.campaign import require_campaign_member
from app.utils.exceptions import AppException
from app.utils.file import validate_file


def create_task_attachment(
    db: Session, task_id: int, file: UploadFile, current_user: User
) -> TaskAttachment:
    task = get_task_by_id(db, task_id)

    if task is None:
        raise AppException(status_code=404, message="Campaign task not found")

    require_campaign_member(db, task.campaign_id, current_user.id)

    if not file.filename:
        raise AppException(status_code=404, message="File name is required")

    original_filename = Path(file.filename).name

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    try:
        validate_file(
            original_filename,
            file_size,
        )
    except ValueError as e:
        raise AppException(
            status_code=400,
            message=str(e),
        )
