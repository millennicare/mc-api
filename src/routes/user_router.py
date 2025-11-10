from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path, Query

from src.core.dependencies.user_dependencies import T_UserDeps
from src.core.deps import T_CurrentUser
from src.schemas.user_schemas import (
    OnboardUserSchema,
    UpdateUserSchema,
    UserInformation,
    UserSchema,
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
async def onboard_user(user: T_CurrentUser, deps: T_UserDeps, body: OnboardUserSchema):
    return await deps.service.onboard_user(user_id=user.id, body=body)


# Leaving these in as examples on how to perform the file upload later for careseeker and caregiver onboarding
# @router.post("/temp")
# async def upload_file(
#     file: Annotated[UploadFile, File(description="Profile picture")], deps: T_UserDeps
# ):
#     await deps.storage_client.upload_file(file=file, key="123")


# @router.get("/temp/{file_id}")
# async def get_file(file_id: str, deps: T_UserDeps):
#     return deps.storage_client.get_presigned_url(file_id)


# @router.delete("/temp/{file_id}")
# async def delete_file(file_id: str, deps: T_UserDeps):
#     deps.storage_client.delete_file(file_id)
