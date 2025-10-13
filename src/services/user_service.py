from uuid import UUID
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user_schemas import CreateUserSchema, UpdateUserSchema, UserSchema


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user: CreateUserSchema) -> User:
        user = await self.user_repository.create_user(user)
        return user

    async def delete_user(self, id: str) -> None:
        await self.user_repository.delete_user(id)

    async def get_users(self, skip: int, limit: int) -> list[UserSchema]:
        users = await self.user_repository.get_users(skip=skip, limit=limit)
        return [UserSchema.model_validate(user) for user in users]

    async def update_user(self, user_id: UUID, body: UpdateUserSchema):
        # update the user's field as usual
        # update the user's roles if roles_to_add or roles_to_remove are provided
        pass
