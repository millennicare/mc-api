from sqlalchemy import insert

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
