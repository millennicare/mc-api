from http import HTTPStatus
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm

from src.core.dependencies.auth_dependencies import T_AuthDeps
from src.core.deps import T_CurrentUser, T_Session
from src.schemas.auth_schemas import (
    ForgotPasswordSchema,
    RefreshTokenRequestSchema,
    ResendVerificationSchema,
    ResetPasswordSchema,
    SignUpSchema,
    TokenResponse,
    VerifySchema,
)
from src.schemas.error_schemas import ErrorDetail
from src.schemas.user_schemas import UserSchema, UserWithInformationSchema

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/sign-up", status_code=HTTPStatus.CREATED, response_model=UserSchema)
async def sign_up(body: SignUpSchema, deps: T_AuthDeps):
    return await deps.service.sign_up(body)


@router.post("/sign-in", status_code=HTTPStatus.OK, response_model=TokenResponse)
async def sign_in(
    body: Annotated[OAuth2PasswordRequestForm, Depends()], deps: T_AuthDeps
):
    return await deps.service.sign_in(email=body.username, password=body.password)


@router.get(
    "/{provider}/login/{role}",
    status_code=HTTPStatus.OK,
    responses={
        400: {"description": "Invalid provider", "model": ErrorDetail},
    },
)
async def oauth_login(
    provider: Literal["google", "apple"],
    role: Literal["careseeker", "caregiver"],
    deps: T_AuthDeps,
):
    """
    Initiates OAuth2 flow with social provider.
    Returns authorization URL with state parameter for CSRF protection.
    """
    return await deps.service.initiate_oauth_login(provider=provider, role=role)


@router.get(
    "/{provider}/callback",
    status_code=HTTPStatus.OK,
    response_model=TokenResponse,
    responses={
        400: {
            "description": "Invalid state or authorization code",
            "model": ErrorDetail,
        },
        401: {"description": "Authentication failed", "model": ErrorDetail},
    },
)
async def oauth_callback(
    provider: Literal["google", "apple"],
    code: Annotated[str, Query(description="Authorization code from provider")],
    state: Annotated[str, Query(description="State parameter for CSRF protection")],
    role: Annotated[
        Literal["careseeker", "caregiver"],
        Query(description="The role they are signing in or up for"),
    ],
    deps: T_AuthDeps,
):
    """
    Handles OAuth2 callback from provider.
    Exchanges code for tokens, creates/updates user, returns your app's tokens.
    """
    return await deps.service.handle_oauth_callback(
        provider=provider, code=code, state=state, role=role
    )


@router.post("/verify", status_code=HTTPStatus.OK, response_model=dict[str, str])
async def verify(body: VerifySchema, deps: T_AuthDeps):
    await deps.service.verify_email(token=body.token, code=body.code)
    return {"message": "Email verified"}


@router.post(
    "/forgot-password", status_code=HTTPStatus.OK, response_model=dict[str, str]
)
async def forgot_password(body: ForgotPasswordSchema, deps: T_AuthDeps):
    await deps.service.forgot_password(email=body.email)
    return {"message": "Password reset email sent"}


@router.patch(
    "/reset-password", status_code=HTTPStatus.OK, response_model=dict[str, str]
)
async def reset_password(body: ResetPasswordSchema, deps: T_AuthDeps):
    await deps.service.reset_password(body)
    return {"message": "Password reset successfully"}


@router.post("/refresh", status_code=HTTPStatus.OK, response_model=TokenResponse)
async def refresh_token(body: RefreshTokenRequestSchema, deps: T_AuthDeps):
    return await deps.service.refresh_token(refresh_token=body.refresh_token)


@router.post(
    "/sign-out",
    status_code=HTTPStatus.OK,
    responses={
        401: {"description": "Unauthorized", "model": ErrorDetail},
    },
)
async def sign_out(
    session: T_Session,
    deps: T_AuthDeps,
):
    return await deps.service.sign_out(session_id=session.id)


@router.get("/me", status_code=HTTPStatus.OK, response_model=UserWithInformationSchema)
async def get_current_user(user: T_CurrentUser, deps: T_AuthDeps):
    return await deps.service.get_me(user_id=user.id)


@router.post(
    "/resend-verification", status_code=HTTPStatus.OK, response_model=dict[str, str]
)
async def resend_verification(body: ResendVerificationSchema, deps: T_AuthDeps):
    await deps.service.resend_verification(email=body.email)
    return {"message": "Verification email sent"}
