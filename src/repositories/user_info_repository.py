from time import perf_counter
from uuid import UUID

from sqlalchemy import insert, select

from src.core.deps import T_Database
from src.core.logger import setup_logger
from src.models.user_information import UserInformation
from src.schemas.user_schemas import OnboardUserSchema

logger = setup_logger(__name__)


class UserInfoRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_user_info(
        self, user_id: UUID, body: OnboardUserSchema
    ) -> UserInformation:
        start = perf_counter()

        statement = (
            insert(UserInformation)
            .values(**body.model_dump(), user_id=user_id)
            .returning(UserInformation)
        )
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"UserInfoRepository.create_user_info took {elapsed_ms:.2f}ms")

        return result.scalar_one()

    async def get_user_info_by_user_id(self, user_id: UUID) -> UserInformation | None:
        start = perf_counter()

        statement = select(UserInformation).where(UserInformation.user_id == user_id)
        result = await self.db.execute(statement)

        elapsed_ms = (perf_counter() - start) * 1000
        logger.info(f"UserInfoRepository.get_user_info_by_user_id took {elapsed_ms:.2f}ms")

        return result.scalar_one_or_none()
