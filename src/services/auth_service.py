from http import HTTPStatus

from fastapi import HTTPException

from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.schemas.auth_schemas import SignInSchema, SignUpSchema
from src.schemas.user_schemas import CreateUserSchema, UserSchema


class AuthService:
    def __init__(
        self, user_repository: UserRepository, role_repository: RoleRepository
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def sign_up(self, body: SignUpSchema):
        existing_user = await self.user_repository.get_user_by_email(email=body.email)
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="A user with this email address already exists",
            )

        role = await self.role_repository.get_role_by_name(str(body.role))
        if role is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Invald role {body.role}",
            )

        # create the user
        create_user_body = CreateUserSchema(body.model_dump_json())
        user = await self.user_repository.create_user(create_user_body)
        print(user)
        # insert into account table with credentials as the provider
        # create the user to role link
        # create a verification code
        # create the session
        # send email

    async def sign_in(self, body: SignInSchema):
        user = await self.user_repository.get_user_by_email(email=body.email)
        if user is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # this shouldn't happen but get the role and if it doesn't exist, throw
        role = await self.role_repository.get_role_by_name(name=str(body.role))
        if role is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Role {str(body.role)} not found",
            )

        await self.user_repository.create_user(UserSchema(**body.model_dump()))
