import enum
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.core.constants import PASSWORD_REGEX


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    CARESEEKER = "careseeker"
    CAREGIVER = "caregiver"


class SignUpSchema(BaseModel):
    email: EmailStr
    password: str
    name: str = Field(min_length=1)
    roles: list[RoleEnum]

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_REGEX.match(value):
            raise ValueError(
                "Password must be 8-64 characters long, contain at least one uppercase letter and one special character (!@#$%^&*)."
            )
        return value


class TokenResponse(BaseModel):
    accessToken: str = Field(alias="access_token")
    refreshtoken: str = Field(alias="refresh_token")


class VerifySchema(BaseModel):
    code: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    password: str

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_REGEX.match(value):
            raise ValueError(
                "Password must be 8-64 characters long, contain at least one uppercase letter and one special character (!@#$%^&*)."
            )
        return value
