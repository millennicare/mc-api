from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateWaitlistSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr


class WaitlistSchema(CreateWaitlistSchema):
    id: UUID
    contacted: bool
    referral_code: str | None = Field(alias="referralCode", default=None)
    notified_at: datetime | None = Field(alias="notifiedAt", default=None)
