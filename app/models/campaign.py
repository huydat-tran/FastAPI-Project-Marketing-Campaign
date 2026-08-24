import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class CampaignMemberRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class ActivityAction(str, enum.Enum):
    CREATE_CAMPAIGN = "CREATE_CAMPAIGN"
    UPDATE_CAMPAIGN = "UPDATE_CAMPAIGN"
    ADD_MEMBER = "ADD_MEMBER"
    REMOVE_MEMBER = "REMOVE_MEMBER"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    owner = relationship(
        "User",
        back_populates="campaigns",
    )

    members = relationship(
        "CampaignMember",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )

    tasks = relationship(
        "CampaignTask",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )

    activity_logs = relationship(
        "ActivityLog",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )


class CampaignMember(Base):
    __tablename__ = "campaign_members"

    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "user_id",
            name="unique_campaign_user",
        ),
    )

    campaign_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("campaigns.id"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True,
    )

    role: Mapped[CampaignMemberRole] = mapped_column(
        Enum(CampaignMemberRole),
        default=CampaignMemberRole.MEMBER,
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    campaign = relationship(
        "Campaign",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="campaign_members",
    )


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    campaign_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("campaigns.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    action: Mapped[ActivityAction] = mapped_column(
        Enum(ActivityAction),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    campaign = relationship(
        "Campaign",
        back_populates="activity_logs",
    )

    user = relationship("User", back_populates="activity_logs")
