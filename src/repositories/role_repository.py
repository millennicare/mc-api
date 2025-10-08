from sqlalchemy import select

from src.core.deps import T_Database
from src.models.role import Role


class RoleRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def get_role_by_name(self, name: str) -> Role | None:
        statement = select(Role).where(Role.name == name)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
