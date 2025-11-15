import uuid
from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException, UploadFile
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.clients.storage import StorageClient
from src.core.logger import setup_logger
from src.models.user_information import UserGenderEnum
from src.repositories.user_info_repository import UserInfoRepository
from src.repositories.user_repository import UserRepository
from src.schemas.user_schemas import (
    CreateUserInformationSchema,
    UpdateUserSchema,
    UserInformation,
    UserSchema,
)


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_info_repository: UserInfoRepository,
        storage_client: StorageClient,
    ):
        self.user_info_repository = user_info_repository
        self.user_repository = user_repository
        self.storage_client = storage_client
        self.logger = setup_logger(name=__name__)

    async def delete_user(self, id: UUID) -> None:
        await self.user_repository.delete_user(id)

    async def get_users(self, skip: int, limit: int) -> list[UserSchema]:
        users = await self.user_repository.get_users(skip=skip, limit=limit)
        return [UserSchema.model_validate(user) for user in users]

    async def update_user(self, user_id: UUID, body: UpdateUserSchema):
        # update the user's field as usual
        # update the user's roles if roles_to_add or roles_to_remove are provided
        pass

    async def get_user(self, user_id: UUID) -> UserSchema:
        user = await self.user_repository.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="User not found"
            )
        return UserSchema.model_validate(user)

    async def onboard_user(
        self,
        user_id: UUID,
        gender: UserGenderEnum,
        phone_number: PhoneNumber,
        birthdate: datetime,
        profile_picture: UploadFile,
    ) -> UserInformation:
        existing_user = await self.user_repository.get_user(user_id=user_id)
        if existing_user is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="User not found"
            )

        existing_user_profile = (
            await self.user_info_repository.get_user_info_by_user_id(user_id)
        )
        if existing_user_profile is not None:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="A profile already exists for this user",
            )

        key = str(uuid.UUID())
        await self.storage_client.upload_file(file=profile_picture, key=key)

        user_info = await self.user_info_repository.create_user_info(
            user_id=existing_user.id,
            body=CreateUserInformationSchema.model_validate(
                {
                    "gender": gender,
                    "phone_number": phone_number,
                    "birthdate": birthdate,
                    "profile_picture": key,
                }
            ),
        )
        return UserInformation.model_validate(user_info)
