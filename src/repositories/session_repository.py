from sqlalchemy import delete, insert, select, update

from src.core.deps import T_Database
from src.models.session import Session
from src.schemas.session_schemas import CreateSessionSchema


class SessionRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_session(self, values: CreateSessionSchema) -> Session:
        statement = insert(Session).values(**values.model_dump()).returning(Session)
        result = await self.db.execute(statement)
        return result.scalar_one()

    async def get_session_by_id(self, session_id) -> Session | None:
        statement = select(Session).where(Session.id == session_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def update_session(self, session_id: str, values: dict) -> None:
        statement = update(Session).where(Session.id == session_id).values(**values)
        await self.db.execute(statement)

    async def delete_session(self, session_id: str) -> None:
        statement = delete(Session).where(Session.id == session_id)
        await self.db.execute(statement)
