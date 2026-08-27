import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.task_attachment import TaskAttachment
from app.models.user import User
from app.services.campaign import require_campaign_member
from app.services.campaign_task import get_task_by_id
from app.utils.exceptions import AppException
from app.utils.file import UPLOAD_DIR, validate_file


def create_task_attachment(
    db: Session, task_id: int, file: UploadFile, current_user: User
) -> TaskAttachment:
    task = get_task_by_id(db, task_id)

    if task is None:
        raise AppException(status_code=404, message="Campaign task not found")

    require_campaign_member(db, task.campaign_id, current_user.id)

    if not file.filename:
        raise AppException(status_code=400, message="File name is required")

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

    stored_filename = f"{uuid.uuid4()}{Path(original_filename).suffix.lower()}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / stored_filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as exc:  # noqa: BLE001
        if file_path.exists():
            file_path.unlink()

        raise AppException(
            status_code=500, message="Failed to save file", detail=str(exc)
        )

    attachment = TaskAttachment(
        task_id=task.id,
        uploaded_by=current_user.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=str(file_path),
        content_type=file.content_type or "application/octet-stream",
        file_size=file_size,
    )

    try:
        db.add(attachment)
        db.commit()
        db.refresh(attachment)

    except Exception:
        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise

    return attachment


def get_task_attachment(
    db: Session, attachment_id: int, current_user: User
) -> TaskAttachment:
    attachment = (
        db.query(TaskAttachment).filter(TaskAttachment.id == attachment_id).first()
    )

    if attachment is None:
        raise AppException(status_code=404, message="Attachment not found")

    task = get_task_by_id(db, attachment.task_id)

    if task is None:
        raise AppException(status_code=404, message="Campaign task not found")

    require_campaign_member(db, task.campaign_id, current_user.id)

    return attachment
