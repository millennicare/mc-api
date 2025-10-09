from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CreateUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    email_verified: bool | None


class UserSchema(CreateUserSchema):
    id: UUID
