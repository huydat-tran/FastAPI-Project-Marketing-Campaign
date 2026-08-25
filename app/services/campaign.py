from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.campaign import (
    ActivityAction,
    ActivityLog,
    Campaign,
    CampaignMember,
    CampaignMemberRole,
)
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate,
    CampaignMemberCreate,
    CampaignUpdate,
)
from app.utils.exceptions import AppException


def get_campaign_by_id(
    db: Session,
    campaign_id: int,
) -> Campaign | None:
    return (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.deleted_at.is_(None),
        )
        .first()
    )


def get_campaign_member(
    db: Session,
    campaign_id: int,
    user_id: int,
) -> CampaignMember | None:
    return (
        db.query(CampaignMember)
        .filter(
            CampaignMember.campaign_id == campaign_id,
            CampaignMember.user_id == user_id,
        )
        .first()
    )


def create_activity_log(
    db: Session,
    campaign_id: int,
    user_id: int,
    action: ActivityAction,
) -> ActivityLog:
    activity_log = ActivityLog(
        campaign_id=campaign_id,
        user_id=user_id,
        action=action,
    )

    db.add(activity_log)

    return activity_log


def create_campaign(
    db: Session,
    data: CampaignCreate,
    current_user: User,
) -> Campaign:
    name = data.name.strip()

    if not name:
        raise AppException(
            status_code=400,
            message="Campaign name cannot be empty",
        )

    campaign = Campaign(
        name=name,
        description=data.description,
        owner_id=current_user.id,
    )

    db.add(campaign)
    db.flush()

    owner_member = CampaignMember(
        campaign_id=campaign.id,
        user_id=current_user.id,
        role=CampaignMemberRole.OWNER,
    )

    db.add(owner_member)

    create_activity_log(
        db=db,
        campaign_id=campaign.id,
        user_id=current_user.id,
        action=ActivityAction.CREATE_CAMPAIGN,
    )

    db.commit()
    db.refresh(campaign)

    return campaign


def get_campaigns(
    db: Session,
    current_user: User,
    search: str | None = None,
) -> list[Campaign]:
    query = (
        db.query(Campaign)
        .join(
            CampaignMember,
            CampaignMember.campaign_id == Campaign.id,
        )
        .filter(
            Campaign.deleted_at.is_(None),
            CampaignMember.user_id == current_user.id,
        )
    )

    if search:
        search = search.strip()

        if search:
            query = query.filter(Campaign.name.ilike(f"%{search}%"))

    return query.order_by(Campaign.id).all()


def get_campaign_detail(
    db: Session,
    campaign_id: int,
) -> Campaign:
    campaign = get_campaign_by_id(
        db,
        campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    return campaign


def update_campaign(
    db: Session,
    campaign_id: int,
    data: CampaignUpdate,
    current_user: User,
) -> Campaign:
    campaign = get_campaign_by_id(
        db,
        campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if "name" in update_data:
        name = update_data["name"].strip()

        if not name:
            raise AppException(
                status_code=400,
                message="Campaign name cannot be empty",
            )

        update_data["name"] = name

    for field, value in update_data.items():
        setattr(
            campaign,
            field,
            value,
        )

    create_activity_log(
        db=db,
        campaign_id=campaign.id,
        user_id=current_user.id,
        action=ActivityAction.UPDATE_CAMPAIGN,
    )

    db.commit()
    db.refresh(campaign)

    return campaign


def delete_campaign(
    db: Session,
    campaign_id: int,
) -> None:
    campaign = get_campaign_by_id(
        db,
        campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    campaign.deleted_at = datetime.now(timezone.utc)

    db.commit()


def add_campaign_member(
    db: Session,
    campaign_id: int,
    data: CampaignMemberCreate,
    current_user: User,
) -> CampaignMember:
    user = (
        db.query(User)
        .filter(
            User.id == data.user_id,
        )
        .first()
    )

    if user is None:
        raise AppException(
            status_code=404,
            message="User not found",
        )

    existing_member = get_campaign_member(
        db,
        campaign_id,
        data.user_id,
    )

    if existing_member is not None:
        raise AppException(
            status_code=400,
            message="User is already a member of this campaign",
        )

    if data.role == CampaignMemberRole.OWNER:
        raise AppException(
            status_code=400,
            message="A new member cannot be assigned the OWNER role",
        )

    member = CampaignMember(
        campaign_id=campaign_id,
        user_id=data.user_id,
        role=CampaignMemberRole.MEMBER,
    )

    db.add(member)

    create_activity_log(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id,
        action=ActivityAction.ADD_MEMBER,
    )

    db.commit()
    db.refresh(member)

    return member


def get_campaign_members(
    db: Session,
    campaign_id: int,
) -> list[CampaignMember]:
    campaign = get_campaign_by_id(
        db,
        campaign_id,
    )

    if campaign is None:
        raise AppException(
            status_code=404,
            message="Campaign not found",
        )

    return (
        db.query(CampaignMember)
        .filter(
            CampaignMember.campaign_id == campaign_id,
        )
        .order_by(CampaignMember.joined_at)
        .all()
    )


def remove_campaign_member(
    db: Session,
    campaign_id: int,
    user_id: int,
    current_user: User,
) -> None:
    member = get_campaign_member(
        db,
        campaign_id,
        user_id,
    )

    if member is None:
        raise AppException(
            status_code=404,
            message="Campaign member not found",
        )

    if member.role == CampaignMemberRole.OWNER:
        raise AppException(
            status_code=400,
            message="The campaign owner cannot be removed",
        )

    db.delete(member)

    create_activity_log(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id,
        action=ActivityAction.REMOVE_MEMBER,
    )

    db.commit()
