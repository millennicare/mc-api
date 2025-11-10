from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.verification_code import VerificationCodeEnum


class CreateVerificationCodeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    value: str
    expires_at: datetime
    user_id: UUID
    identifier: VerificationCodeEnum
    token: str


class VerificationCodeSchema(CreateVerificationCodeSchema):
    id: UUID
