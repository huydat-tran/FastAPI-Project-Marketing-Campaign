from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate,
    CampaignMemberCreate,
    CampaignMemberResponse,
    CampaignResponse,
    CampaignUpdate,
)
from app.services.campaign import (
    add_campaign_member,
    create_campaign,
    delete_campaign,
    get_campaign_detail,
    get_campaign_members,
    get_campaigns,
    remove_campaign_member,
    update_campaign,
)

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_new_campaign(
    data: CampaignCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return create_campaign(db, data, current_user)


@router.get("", response_model=list[CampaignResponse])
def list_my_campaign(
    search: str | None = Query(default=None, description="Search by campaign's name"),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_campaigns(db, current_user, search)


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_campaign_detail(db, campaign_id, current_user)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
def update_existing_campaign(
    campaign_id: int,
    data: CampaignUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return update_campaign(db, campaign_id, data, current_user)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    delete_campaign(db, campaign_id, current_user)


@router.post(
    "/{campaign_id}/members",
    response_model=CampaignMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    campaign_id: int,
    data: CampaignMemberCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return add_campaign_member(db, campaign_id, data, current_user)


@router.get("/{campaign_id}/members", response_model=list[CampaignMemberResponse])
def list_member(
    campaign_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return get_campaign_members(db, campaign_id, current_user)


@router.delete(
    "/{campaign_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_member(
    campaign_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    remove_campaign_member(
        db,
        campaign_id,
        user_id,
        current_user,
    )
