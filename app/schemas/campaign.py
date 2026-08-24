from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.campaign import CampaignMemberRole


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class CampaignUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = None


class CampaignResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignMemberCreate(BaseModel):
    user_id: int


class CampaignMemberResponse(BaseModel):
    campaign_id: int
    user_id: int
    role: CampaignMemberRole
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
