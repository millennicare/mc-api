from uuid import UUID
from sqlalchemy import select

from src.core.deps import T_Database
from src.models.role import Role
from src.models.user_to_role import user_to_role


class RoleRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def get_role_by_name(self, name: str) -> Role | None:
        statement = select(Role).where(Role.name == name)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_roles_by_user_id(self, user_id: UUID) -> list[Role]:
        statement = (
            select(Role)
            .join(user_to_role, user_to_role.c.role_id == Role.id)
            .where(user_to_role.c.user_id == user_id)
        )
        result = await self.db.scalars(statement)
        return list(result.all())
