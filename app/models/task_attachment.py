from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

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

    uploaded_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    task = relationship(
        "CampaignTask",
        back_populates="attachments",
    )

    uploader = relationship(
        "User",
    )
