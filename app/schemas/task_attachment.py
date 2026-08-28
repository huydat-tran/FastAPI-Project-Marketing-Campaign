from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskAttachmentResponse(BaseModel):
    id: int
    task_id: int
    original_filename: str
    stored_filename: str
    content_type: str
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
