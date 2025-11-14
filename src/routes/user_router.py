from datetime import datetime
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, Path, Query, UploadFile
from pydantic import AfterValidator
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.core.dependencies.user_dependencies import T_UserDeps
from src.core.deps import T_CurrentUser
from src.models.user_information import UserGenderEnum
from src.schemas.user_schemas import (
    UpdateUserSchema,
    UserInformation,
    UserSchema,
    is_over_eighteen,
)

router = APIRouter(tags=["user"], prefix="/users")


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: Annotated[UUID, Path(title="The id of the user")],
    deps: T_UserDeps,
):
    return await deps.service.delete_user(id=user_id)


@router.get("", status_code=HTTPStatus.OK, response_model=list[UserSchema])
async def get_users(
    deps: T_UserDeps,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
):
    return await deps.service.get_users(skip, limit)


@router.patch("/{user_id}")
async def update_user(
    user_id: Annotated[UUID, Path(title="The id of the user")],
    deps: T_UserDeps,
    body: UpdateUserSchema,
):
    return await deps.service.update_user(user_id=user_id, body=body)


@router.get("/{user_id}", status_code=HTTPStatus.OK, response_model=UserSchema)
async def get_user(
    user_id: Annotated[UUID, Path(title="The id of the user")],
    deps: T_UserDeps,
):
    return await deps.service.get_user(user_id)


@router.post("/onboard", status_code=HTTPStatus.CREATED, response_model=UserInformation)
async def onboard_user(
    user: T_CurrentUser,
    deps: T_UserDeps,
    gender: Annotated[UserGenderEnum, Form()],
    phone_number: Annotated[PhoneNumber, Form()],
    birthdate: Annotated[datetime, AfterValidator(is_over_eighteen)],
    profile_picture: Annotated[UploadFile, File()],
):
    return await deps.service.onboard_user(
        user_id=user.id,
        gender=gender,
        phone_number=phone_number,
        birthdate=birthdate,
        profile_picture=profile_picture,
    )
