from uuid import UUID

from sqlalchemy import insert, select

from src.core.deps import T_Database
from src.models.user_to_role import user_to_role


class UserToRoleRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_user_to_role(self, user_id: UUID, role_id: UUID) -> None:
        statement = insert(user_to_role).values(user_id=user_id, role_id=role_id)
        await self.db.execute(statement)

    async def user_has_role(self, user_id: UUID, role_id: UUID) -> bool:
        statement = select(user_to_role).where(
            user_to_role.c.user_id == user_id, user_to_role.c.role_id == role_id
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none() is not None
