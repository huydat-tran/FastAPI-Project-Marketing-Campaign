from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.campaign_task import TaskPriority, TaskStatus


class CampaignTaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None


class CampaignTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None


class CampaignTaskResponse(BaseModel):
    id: int
    campaign_id: int
    title: str
    description: str | None
    assignee_id: int | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
