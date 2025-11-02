from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CreateWaitlistSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr


class WaitlistSchema(CreateWaitlistSchema):
    id: UUID
