from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.campaign import (
    require_campaign_member,
    require_task_owner_or_assignee,
)
from app.models.campaign_task import (
    CampaignTaskPriority,
    CampaignTaskStatus,
)
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
    prefix="/campaigns",
    tags=["Campaign Tasks"],
)


@router.post(
    "/{campaign_id}/campaign-tasks",
    response_model=CampaignTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    campaign_id: int,
    data: CampaignTaskCreate,
    current_user: User = Depends(require_campaign_member),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return create_campaign_task(
        db,
        campaign_id,
        data,
        current_user,
    )


@router.get(
    "/{campaign_id}/campaign-tasks",
    response_model=list[CampaignTaskResponse],
)
def list_tasks(
    campaign_id: int,
    search: str | None = Query(default=None),
    status: CampaignTaskStatus | None = Query(default=None),
    priority: CampaignTaskPriority | None = Query(default=None),
    assignee_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: User = Depends(require_campaign_member),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_campaign_tasks(
        db=db,
        campaign_id=campaign_id,
        current_user=current_user,
        search=search,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        limit=limit,
        offset=offset,
        sort=sort,
        order=order,
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
    current_user: User = Depends(require_task_owner_or_assignee),  # noqa: B008
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
    current_user: User = Depends(require_task_owner_or_assignee),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    delete_campaign_task(
        db,
        task_id,
        current_user,
    )
    return None
