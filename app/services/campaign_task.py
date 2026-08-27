from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.campaign_task import CampaignTask
from app.models.user import User
from app.schemas.campaign_task import (
    CampaignTaskCreate,
    CampaignTaskUpdate,
)
from app.services.campaign import (
    get_campaign_member,
    require_campaign_member,
)
from app.utils.exceptions import AppException


def get_task_by_id(
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


def require_task_member(
    db: Session,
    task_id: int,
    user_id: int,
) -> CampaignTask:
    task = get_task_by_id(db, task_id)

    if task is None:
        raise AppException(
            status_code=404,
            message="Campaign task not found",
        )

    require_campaign_member(
        db,
        task.campaign_id,
        user_id,
    )

    return task


def validate_assignee(
    db: Session,
    campaign_id: int,
    assignee_id: int | None,
) -> None:
    if assignee_id is None:
        return

    user = (
        db.query(User)
        .filter(
            User.id == assignee_id,
        )
        .first()
    )

    if user is None:
        raise AppException(
            status_code=404,
            message="Assignee user not found",
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


def create_campaign_task(
    db: Session,
    campaign_id: int,
    data: CampaignTaskCreate,
    current_user: User,
) -> CampaignTask:
    require_campaign_member(
        db,
        campaign_id,
        current_user.id,
    )

    validate_assignee(
        db,
        campaign_id,
        data.assignee_id,
    )

    title = data.title.strip()

    if not title:
        raise AppException(
            status_code=400,
            message="Task title cannot be empty",
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
    current_user: User,
    status: str | None = None,
    priority: str | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> list[CampaignTask]:
    require_campaign_member(
        db,
        campaign_id,
        current_user.id,
    )

    query = db.query(CampaignTask).filter(
        CampaignTask.campaign_id == campaign_id,
    )

    if status is not None:
        query = query.filter(
            CampaignTask.status == status,
        )

    if priority is not None:
        query = query.filter(
            CampaignTask.priority == priority,
        )

    if assignee_id is not None:
        query = query.filter(
            CampaignTask.assignee_id == assignee_id,
        )

    if search:
        search = search.strip()

        if search:
            query = query.filter(
                CampaignTask.title.ilike(f"%{search}%"),
            )

    if sort_by == "due_date":
        sort_column = CampaignTask.due_date
    elif sort_by == "created_at":
        sort_column = CampaignTask.created_at
    else:
        raise AppException(
            status_code=400, message="Can only sort by created_at and due_date"
        )

    if sort_order.lower() == "asc":
        query = query.order_by(
            asc(sort_column),
        )
    elif sort_order.lower() == "desc":
        query = query.order_by(
            desc(sort_column),
        )
    else:
        raise AppException(
            status_code=400, message="Invalid sort order. Allowed values: asc, desc"
        )

    return query.offset(offset).limit(limit).all()


def get_campaign_task_detail(
    db: Session,
    task_id: int,
    current_user: User,
) -> CampaignTask:
    return require_task_member(
        db,
        task_id,
        current_user.id,
    )


def update_campaign_task(
    db: Session,
    task_id: int,
    data: CampaignTaskUpdate,
    current_user: User,
) -> CampaignTask:
    task = require_task_member(
        db,
        task_id,
        current_user.id,
    )

    if (
        task.campaign.owner_id != current_user.id
        and task.assignee_id != current_user.id
    ):
        raise AppException(
            status_code=403,
            message="You don't have permission to update this task",
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
        if task.campaign.owner_id != current_user.id:
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
    current_user: User,
) -> None:
    task = require_task_member(
        db,
        task_id,
        current_user.id,
    )

    if task.campaign.owner_id != current_user.id:
        raise AppException(
            status_code=403,
            message="Only the campaign owner can delete this task",
        )

    db.delete(task)
    db.commit()
