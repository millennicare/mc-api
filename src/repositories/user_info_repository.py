from uuid import UUID

from sqlalchemy import insert, select

from src.core.deps import T_Database
from src.models.user_information import UserInformation
from src.schemas.user_schemas import OnboardUserSchema


class UserInfoRepository:
    def __init__(self, db: T_Database):
        self.db = db

    async def create_user_info(
        self, user_id: UUID, body: OnboardUserSchema
    ) -> UserInformation:
        statement = (
            insert(UserInformation)
            .values(**body.model_dump(), user_id=user_id)
            .returning(UserInformation)
        )
        result = await self.db.execute(statement)
        return result.scalar_one()

    async def get_user_info_by_user_id(self, user_id: UUID) -> UserInformation | None:
        statement = select(UserInformation).where(UserInformation.user_id == user_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
