from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.core.dependencies.auth_dependencies import T_AuthDeps
from src.core.deps import T_CurrentUser, T_Session
from src.schemas.auth_schemas import (
    ForgotPasswordSchema,
    RefreshTokenRequestSchema,
    ResetPasswordSchema,
    SignUpSchema,
    TokenResponse,
    VerifySchema,
)
from src.schemas.user_schemas import UserSchema

router = APIRouter(tags=["auth"], prefix="/api/auth")


@router.post(
    "/sign-up",
    status_code=HTTPStatus.CREATED,
    responses={
        201: {"description": "User created"},
        404: {"description": "Role not found"},
        409: {"description": "A user already exists with this email address"},
    },
    response_model=UserSchema,
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
    return await deps.service.verify_email(code=body.code, user_id=user.id)


@router.post("/forgot-password", status_code=HTTPStatus.OK)
async def forgot_password(body: ForgotPasswordSchema, deps: T_AuthDeps):
    return await deps.service.forgot_password(body)


@router.patch("/reset-password", status_code=HTTPStatus.OK)
async def reset_password(body: ResetPasswordSchema, deps: T_AuthDeps):
    return await deps.service.reset_password(body)


@router.post("/refresh", status_code=HTTPStatus.OK, response_model=TokenResponse)
async def refresh_token(body: RefreshTokenRequestSchema, deps: T_AuthDeps):
    return await deps.service.refresh_token(refresh_token=body.refresh_token)


@router.post("/sign-out", status_code=HTTPStatus.OK)
async def sign_out(session: T_Session, deps: T_AuthDeps):
    return await deps.service.sign_out(session_id=session.id)


@router.get("/me", status_code=HTTPStatus.OK, response_model=UserSchema)
async def get_current_user(user: T_CurrentUser):
    return user
