import enum
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.core.constants import PASSWORD_REGEX


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    CARESEEKER = "careseeker"
    CAREGIVER = "caregiver"


class TokenBase(BaseModel):
    sub: str
    sessionId: str
    exp: datetime
    iat: datetime


class AccessToken(TokenBase):
    roles: list[str]
    type: Literal["access"]


class RefreshToken(TokenBase):
    type: Literal["refresh"]


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
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")


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


class RefreshTokenRequestSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    refresh_token: str = Field(alias="refreshToken")
