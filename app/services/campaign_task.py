from sqlalchemy.orm import Session

from app.models.campaign import CampaignMemberRole
from app.models.campaign_task import CampaignTask
from app.models.user import User
from app.schemas.campaign_task import (
    CampaignTaskCreate,
    CampaignTaskUpdate,
)
from app.services.campaign import (
    get_campaign_by_id,
    get_campaign_member,
)
from app.services.user import get_user_by_id
from app.utils.exceptions import AppException


def get_campaign_task_by_id(
    db: Session,
    task_id: int,
) -> CampaignTask | None:
    return (
        db.query(CampaignTask)
        .filter(
            CampaignTask.id == task_id,
        )
        .first()
    )


def validate_assignee(
    db: Session,
    campaign_id: int,
    assignee_id: int | None,
) -> None:
    if assignee_id is None:
        return

    user = get_user_by_id(
        db,
        assignee_id,
    )

    if user is None:
        raise AppException(
            status_code=404,
            message="Assignee not found",
        )

    member = get_campaign_member(
        db,
        campaign_id,
        assignee_id,
    )

    if member is None:
        raise AppException(
            status_code=400,
            message="Assignee must be a member of this campaign",
        )

    if not user.is_active:
        raise AppException(
            status_code=400,
            message="Assignee account is inactive",
        )


def create_campaign_task(
    db: Session,
    campaign_id: int,
    data: CampaignTaskCreate,
    current_user: User,
) -> CampaignTask:
    campaign = get_campaign_by_id(
        db,
        campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    title = data.title.strip()

    if not title:
        raise AppException(
            status_code=400,
            message="Task title cannot be empty",
        )

    validate_assignee(
        db,
        campaign_id,
        data.assignee_id,
    )

    task = CampaignTask(
        campaign_id=campaign_id,
        title=title,
        description=data.description,
        assignee_id=data.assignee_id,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
    )

    db.add(task)

    db.commit()
    db.refresh(task)

    return task


def get_campaign_tasks(
    db: Session,
    campaign_id: int,
    search: str | None = None,
    status=None,
    priority=None,
    assignee_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
    sort: str = "created_at",
    order: str = "desc",
) -> list[CampaignTask]:
    campaign = get_campaign_by_id(
        db,
        campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    query = db.query(CampaignTask).filter(
        CampaignTask.campaign_id == campaign_id,
    )

    if search:
        search = search.strip()

        if search:
            query = query.filter(CampaignTask.title.ilike(f"%{search}%"))

    if status is not None:
        query = query.filter(CampaignTask.status == status)

    if priority is not None:
        query = query.filter(CampaignTask.priority == priority)

    if assignee_id is not None:
        query = query.filter(CampaignTask.assignee_id == assignee_id)

    sort_columns = {
        "created_at": CampaignTask.created_at,
        "due_date": CampaignTask.due_date,
    }

    sort_column = sort_columns.get(sort)

    if sort_column is None:
        raise AppException(
            status_code=400,
            message="Invalid sort field. Allowed values: created_at, due_date",
        )

    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    elif order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        raise AppException(
            status_code=400,
            message="Invalid sort order. Allowed values: asc, desc",
        )

    return query.offset(offset).limit(limit).all()


def get_campaign_task_detail(
    db: Session,
    task_id: int,
) -> CampaignTask:
    task = get_campaign_task_by_id(
        db,
        task_id,
    )

    if task is None:
        raise AppException(
            status_code=404,
            message="Campaign task not found",
        )

    campaign = get_campaign_by_id(
        db,
        task.campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    return task


def update_campaign_task(
    db: Session,
    task_id: int,
    data: CampaignTaskUpdate,
    current_user: User,
) -> CampaignTask:
    task = get_campaign_task_by_id(
        db,
        task_id,
    )

    if task is None:
        raise AppException(
            status_code=404,
            message="Campaign task not found",
        )

    campaign = get_campaign_by_id(
        db,
        task.campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if "title" in update_data:
        title = update_data["title"].strip()

        if not title:
            raise AppException(
                status_code=400,
                message="Task title cannot be empty",
            )

        update_data["title"] = title

    if "assignee_id" in update_data:
        member = get_campaign_member(
            db,
            task.campaign_id,
            current_user.id,
        )

        if member is None:
            raise AppException(
                status_code=403,
                message="You are not a member of this campaign",
            )

        if member.role != CampaignMemberRole.OWNER:
            raise AppException(
                status_code=403,
                message="Only the campaign owner can change the assignee",
            )

        validate_assignee(
            db,
            task.campaign_id,
            update_data["assignee_id"],
        )

    for field, value in update_data.items():
        setattr(
            task,
            field,
            value,
        )

    db.commit()
    db.refresh(task)

    return task


def delete_campaign_task(
    db: Session,
    task_id: int,
) -> None:
    task = get_campaign_task_by_id(
        db,
        task_id,
    )

    if task is None:
        raise AppException(
            status_code=404,
            message="Campaign task not found",
        )

    campaign = get_campaign_by_id(
        db,
        task.campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    db.delete(task)

    db.commit()
