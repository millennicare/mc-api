from time import perf_counter
from uuid import UUID

from sqlalchemy import delete, insert, select, update

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.user import User
from src.schemas.user_schemas import CreateUserSchema

logger = setup_logger(name=__name__)

class UserRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def get_user(self, user_id: UUID) -> User | None:
        start = perf_counter()

        statement = select(User).where(User.id == user_id)
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"UserRepository.get_user took {elapsed_ms:.2f}ms")

        return result.scalar_one_or_none()

    async def create_user(self, values: CreateUserSchema) -> User:
        start = perf_counter()

        statement = insert(User).values(**values.model_dump()).returning(User)
        result = await self.db.execute(statement)
        await self.db.commit()

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"UserRepository.create_user took {elapsed_ms:.2f}ms")

        return result.scalar_one()

    async def get_user_by_email(self, email: str) -> User | None:
        start = perf_counter()

        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"UserRepository.get_user_by_email took {elapsed_ms:.2f}ms")

        return result.scalar_one_or_none()

    async def delete_user(self, id: UUID) -> None:
        start = perf_counter()

        statement = delete(User).where(User.id == id)
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"UserRepository.delete_user took {elapsed_ms:.2f}ms")

    async def get_users(self, skip: int, limit: int) -> list[User]:
        start = perf_counter()

        statement = select(User).limit(limit).offset(skip)
        result = await self.db.scalars(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"UserRepository.get_users took {elapsed_ms:.2f}ms")

        return list(result.all())

    async def update_user(self, user_id: UUID, values: dict) -> User:
        start = perf_counter()

        statement = (
            update(User).where(User.id == user_id).values(**values).returning(User)
        )
        result = await self.db.execute(statement)
        await self.db.commit()

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"UserRepository.update_user took {elapsed_ms:.2f}ms")

        return result.scalar_one()
