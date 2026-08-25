from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskCommentCreate(BaseModel):
    content: str


class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
