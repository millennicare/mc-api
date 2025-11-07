from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.contact import ContactPriorityEnum, ContactStatusEnum


class CreateContactSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, use_enum_values=True
    )

    full_name: str = Field(alias="fullName")
    email: EmailStr
    message: str
    user_id: UUID | None = Field(alias="userId", default=None)


class ContactSchema(CreateContactSchema):
    id: UUID
    status: ContactStatusEnum
    priority: ContactPriorityEnum
    submitted_at: datetime = Field(alias="submittedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime | None = Field(alias="updatedAt", default=None)
