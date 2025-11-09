from time import perf_counter
from uuid import UUID

from sqlalchemy import delete, insert, select, update

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.session import Session
from src.schemas.session_schemas import CreateSessionSchema

logger = setup_logger(__name__)


class SessionRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_session(self, values: CreateSessionSchema) -> Session:
        start = perf_counter()

        statement = insert(Session).values(**values.model_dump()).returning(Session)
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"SessionRepository.create_session took {elapsed_ms:.2f}ms")

        return result.scalar_one()

    async def get_session_by_id(self, session_id) -> Session | None:
        start = perf_counter()

        statement = select(Session).where(Session.id == session_id)
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"SessionRepository.get_session_by_id took {elapsed_ms:.2f}ms")

        return result.scalar_one_or_none()

    async def update_session(self, session_id: UUID, values: dict) -> None:
        start = perf_counter()

        statement = update(Session).where(Session.id == session_id).values(**values)
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"SessionRepository.update_session took {elapsed_ms:.2f}ms")

    async def delete_session(self, session_id: str) -> None:
        start = perf_counter()

        statement = delete(Session).where(Session.id == session_id)
        await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"SessionRepository.delete_session took {elapsed_ms:.2f}ms")
