from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateAccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: str
    provider_id: str
    user_id: UUID
    access_token: str | None = None
    refresh_token: str | None = None
    id_token: str | None = None
    access_token_expires_at: int | None = None
    refresh_token_expires_at: int | None = None
    scope: str | None = None
    password: str | None = None


class Account(CreateAccountSchema):
    id: UUID
