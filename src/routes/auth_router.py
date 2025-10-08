from http import HTTPStatus

from fastapi import APIRouter

from src.core.dependencies.auth_dependencies import T_AuthDeps
from src.schemas.auth_schemas import SignInSchema, SignUpSchema

router = APIRouter(tags=["auth"], prefix="/api/auth")


@router.post("/sign-up", status_code=HTTPStatus.CREATED)
async def sign_up(body: SignUpSchema, deps: T_AuthDeps):
    return await deps.service.sign_up(body)


@router.post("/sign-in", status_code=HTTPStatus.OK)
async def sign_in(body: SignInSchema, deps: T_AuthDeps):
    return await deps.service.sign_in(body)
