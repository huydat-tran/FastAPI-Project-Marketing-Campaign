from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TaskComment(Base):
    __tablename__ = "task_comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("campaign_tasks.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    task = relationship(
        "CampaignTask",
        back_populates="comments",
    )

    user = relationship(
        "User",
    )
