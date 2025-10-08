from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.core.constants import PASSWORD_REGEX


class SignUpSchema(BaseModel):
    email: EmailStr
    password: str
    role: Literal["careseeker", "caregiver", "admin"]
    name: str = Field(min_length=1)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_REGEX.match(value):
            raise ValueError(
                "Password must be 8-64 characters long, contain at least one uppercase letter and one special character (!@#$%^&*)."
            )
        return value


class SignInSchema(BaseModel):
    email: EmailStr
    password: str
    role: Literal["careseeker", "caregiver", "admin"]
