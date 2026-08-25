from fastapi import Depends, Path
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.campaign import CampaignMemberRole
from app.models.user import User
from app.services.campaign import (
    get_campaign_by_id,
    get_campaign_member,
)
from app.services.campaign_task import get_campaign_task_by_id
from app.utils.exceptions import AppException


def require_campaign_member(
    campaign_id: int = Path(...),
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> User:
    campaign = get_campaign_by_id(db, campaign_id)

    if campaign is None:
        raise AppException(status_code=404, message="Campaign not found")

    member = get_campaign_member(db, campaign_id, current_user.id)

    if member is None:
        raise AppException(
            status_code=403, message="You are not a member of this campaign"
        )

    return current_user


def require_campaign_owner(
    campaign_id: int = Path(...),
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> User:
    campaign = get_campaign_by_id(db, campaign_id)

    if campaign is None:
        raise AppException(status_code=404, message="Campaign not found")

    if campaign.owner_id != current_user.id:
        raise AppException(
            status_code=403, message="Only the campaign owner can perform this action"
        )

    return current_user


def require_task_owner_or_assignee(
    task_id: int = Path(...),
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> User:
    task = get_campaign_task_by_id(db, task_id)

    if task is None:
        raise AppException(status_code=404, message="Campaign task not found")

    campaign = get_campaign_by_id(db, task.campaign_id)

    if campaign is None:
        raise AppException(status_code=404, message="Campaign not found")

    member = get_campaign_member(db, task.campaign_id, current_user.id)

    if member is None:
        raise AppException(
            status_code=403,
            message="You are not a member of this campaign",
        )

    if member.role != CampaignMemberRole.OWNER and task.assignee_id != current_user.id:
        raise AppException(
            status_code=403, message="You don't have permission to perform this action"
        )

    return current_user
