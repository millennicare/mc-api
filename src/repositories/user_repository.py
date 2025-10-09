from sqlalchemy import delete, insert, select

from src.core.deps import T_Database
from src.models.user import User
from src.schemas.user_schemas import CreateUserSchema


class UserRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_user(self, values: CreateUserSchema) -> User:
        statement = insert(User).values(**values.model_dump()).returning(User)
        result = await self.db.execute(statement)
        await self.db.commit()
        return result.scalar_one()

    async def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def delete_user(self, id: str) -> None:
        statement = delete(User).where(User.id == id)
        await self.db.execute(statement)

    async def get_users(self, skip: int, limit: int) -> list[User]:
        statement = select(User).limit(limit).offset(skip)
        result = await self.db.scalars(statement)
        return list(result.all())
