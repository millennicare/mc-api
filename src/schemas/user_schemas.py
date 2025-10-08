from pydantic import BaseModel, EmailStr


class CreateUserSchema(BaseModel):
    name: str
    email: EmailStr
    email_verified: bool | None


class UserSchema(CreateUserSchema):
    id: str
