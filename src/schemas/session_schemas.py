from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.session import SessionRoleEnum


class CreateSessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expires_at: datetime
    user_id: UUID
    role: SessionRoleEnum


class SessionSchema(CreateSessionSchema):
    id: UUID
