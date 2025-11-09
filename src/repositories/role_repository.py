from time import perf_counter
from uuid import UUID

from sqlalchemy import select

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.role import Role
from src.models.user_to_role import user_to_role

logger = setup_logger(__name__)

class RoleRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def get_role_by_name(self, name: str) -> Role | None:
        start = perf_counter()

        statement = select(Role).where(Role.name == name)
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"RoleRepository.get_role_by_name took {elapsed_ms:.2f}ms")

        return result.scalar_one_or_none()

    async def get_roles_by_user_id(self, user_id: UUID) -> list[Role]:
        start = perf_counter()

        statement = (
            select(Role)
            .join(user_to_role, user_to_role.c.role_id == Role.id)
            .where(user_to_role.c.user_id == user_id)
        )
        result = await self.db.scalars(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"RoleRepository.get_roles_by_user_id took {elapsed_ms:.2f}ms")

        return list(result.all())
