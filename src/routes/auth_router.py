from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.core.dependencies.auth_dependencies import T_AuthDeps
from src.core.deps import T_CurrentUser
from src.schemas.auth_schemas import (
    SignUpSchema,
    TokenResponse,
    VerifySchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
)

router = APIRouter(tags=["auth"], prefix="/api/auth")


@router.post(
    "/sign-up",
    status_code=HTTPStatus.CREATED,
    responses={
        201: {"description": "User created"},
        404: {"description": "Role not found"},
        409: {"description": "A user already exists with this email address"},
    },
)
async def sign_up(body: SignUpSchema, deps: T_AuthDeps):
    return await deps.service.sign_up(body)


@router.post("/sign-in", status_code=HTTPStatus.OK, response_model=TokenResponse)
async def sign_in(
    body: Annotated[OAuth2PasswordRequestForm, Depends()], deps: T_AuthDeps
):
    return await deps.service.sign_in(email=body.username, password=body.password)


@router.post("/verify", status_code=HTTPStatus.OK)
async def verify(body: VerifySchema, deps: T_AuthDeps, user: T_CurrentUser):
    return await deps.service.verify_email(code=body.code, user_id=user["user_id"])


@router.post("/forgot-password", status_code=HTTPStatus.OK)
async def forgot_password(body: ForgotPasswordSchema, deps: T_AuthDeps):
    return await deps.service.forgot_password(body)


@router.patch("/reset-password", status_code=HTTPStatus.OK)
async def reset_password(body: ResetPasswordSchema, deps: T_AuthDeps):
    return await deps.service.reset_password(body)


@router.post("/refresh", status_code=HTTPStatus.OK)
async def refresh_token(token: str, deps: T_AuthDeps):
    return await deps.service.refresh_token(token)


@router.post("/sign-out", status_code=HTTPStatus.OK)
async def sign_out(token: str, deps: T_AuthDeps):
    return await deps.service.sign_out(token)
