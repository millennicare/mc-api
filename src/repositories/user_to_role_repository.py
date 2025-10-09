from uuid import UUID

from sqlalchemy import insert

from src.core.deps import T_Database
from src.models.user_to_role import user_to_role


class UserToRoleRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_user_to_role(self, user_id: UUID, role_id: UUID) -> None:
        statement = insert(user_to_role).values(user_id=user_id, role_id=role_id)
        await self.db.execute(statement)
