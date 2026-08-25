from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.campaign_task import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.campaign_task import (
    CampaignTaskCreate,
    CampaignTaskResponse,
    CampaignTaskUpdate,
)
from app.services.campaign_task import (
    create_campaign_task,
    delete_campaign_task,
    get_campaign_task_detail,
    get_campaign_tasks,
    update_campaign_task,
)

router = APIRouter(
    tags=["Campaign Tasks"],
)


@router.post(
    "/campaigns/{campaign_id}/campaign-tasks",
    response_model=CampaignTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    campaign_id: int,
    data: CampaignTaskCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return create_campaign_task(
        db,
        campaign_id,
        data,
        current_user,
    )


@router.get(
    "/campaigns/{campaign_id}/campaign-tasks",
    response_model=list[CampaignTaskResponse],
)
def list_tasks(
    campaign_id: int,
    task_status: TaskStatus | None = Query(  # noqa: B008
        default=None,
        alias="status",
        description="Filter by task status",
    ),
    priority: TaskPriority | None = Query(  # noqa: B008
        default=None,
        description="Filter by task priority",
    ),
    assignee_id: int | None = Query(
        default=None,
        description="Filter by assignee user ID",
    ),
    search: str | None = Query(
        default=None,
        description="Search task title",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of tasks to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of tasks to skip",
    ),
    sort_by: str = Query(
        default="created_at",
        pattern="^(created_at|due_date)$",
        description="Sort by created_at or due_date",
    ),
    sort_order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort direction",
    ),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_campaign_tasks(
        db=db,
        campaign_id=campaign_id,
        current_user=current_user,
        status=task_status,
        priority=priority,
        assignee_id=assignee_id,
        search=search,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/campaign-tasks/{task_id}",
    response_model=CampaignTaskResponse,
)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_campaign_task_detail(
        db,
        task_id,
        current_user,
    )


@router.patch(
    "/campaign-tasks/{task_id}",
    response_model=CampaignTaskResponse,
)
def update_task(
    task_id: int,
    data: CampaignTaskUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return update_campaign_task(
        db,
        task_id,
        data,
        current_user,
    )


@router.delete(
    "/campaign-tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    delete_campaign_task(
        db,
        task_id,
        current_user,
    )
