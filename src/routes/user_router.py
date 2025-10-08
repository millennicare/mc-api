from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.params import Path
from src.schemas.user_schemas import UserSchema
from src.core.dependencies.user_dependencies import T_UserDeps

router = APIRouter(tags=["user"], prefix="/api/users")


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: Annotated[str, Path(title="The id of the user")], deps: T_UserDeps
):
    return await deps.service.delete_user(user_id)


@router.get("/", status_code=HTTPStatus.OK, response_model=list[UserSchema])
async def get_users(
    deps: T_UserDeps,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
):
    return await deps.service.get_users(skip, limit)
