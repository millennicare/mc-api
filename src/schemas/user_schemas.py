from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.models.user_information import UserGenderEnum
from src.schemas.auth_schemas import RoleEnum


class CreateUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    first_name: str = Field(min_length=1, alias="firstName")
    last_name: str = Field(min_length=1, alias="lastName")
    email: EmailStr
    email_verified: bool | None = Field(alias="emailVerified", default=False)


class UserSchema(CreateUserSchema):
    id: UUID


class AddRoleToUserSchema(BaseModel):
    user_id: UUID
    role: RoleEnum


class UpdateUserSchema(BaseModel):
    first_name: str | None = Field(alias="firstName", default=None)
    last_name: str | None = Field(alias="lastName", default=None)
    email: EmailStr | None = None
    roles_to_add: list[RoleEnum] | None = Field(alias="rolesToAdd", default=None)
    roles_to_remove: list[RoleEnum] | None = Field(alias="rolesToRemove", default=None)


def is_over_eighteen(v: datetime):
    today = date.today()
    birthdate = v.date() if isinstance(v, datetime) else v
    age = (
        today.year
        - birthdate.year
        - ((today.month, today.day) < (birthdate.month, birthdate.day))
    )

    if age < 18:
        raise ValueError("User must be at least 18 years old")

    return v


class OnboardUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    gender: UserGenderEnum
    phone_number: PhoneNumber = Field(alias="phoneNumber")
    birthdate: Annotated[datetime, AfterValidator(is_over_eighteen)]


class UserInformation(OnboardUserSchema):
    id: UUID
    user_id: UUID = Field(alias="userId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime | None = Field(alias="updatedAt", default=None)
