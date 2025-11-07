import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactPriorityEnum(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ContactStatusEnum(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CreateContactSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str = Field(alias="fullName")
    email: EmailStr
    message: str
    submitted_at: datetime = Field(alias="submittedAt", default=datetime.now())
    user_id: UUID | None = Field(alias="userId", default=None)


class ContactSchema(CreateContactSchema):
    id: UUID
    status: ContactStatusEnum = Field(alias="status")
    priority: ContactPriorityEnum = Field(alias="priority")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime | None = Field(alias="updatedAt", default=None)
