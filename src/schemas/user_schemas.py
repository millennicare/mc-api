from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from src.schemas.auth_schemas import RoleEnum


class CreateUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    email_verified: bool | None


class UserSchema(CreateUserSchema):
    id: UUID


class AddRoleToUserSchema(BaseModel):
    user_id: UUID
    role: RoleEnum


class UpdateUserSchema(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    roles_to_add: list[RoleEnum] | None = Field(alias="rolesToAdd", default=None)
    roles_to_remove: list[RoleEnum] | None = Field(alias="rolesToRemove", default=None)
