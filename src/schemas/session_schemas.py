from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateSessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expires_at: datetime
    user_id: UUID


class SessionSchema(CreateSessionSchema):
    id: UUID
