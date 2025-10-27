"""
Global dependencies
"""

from datetime import datetime, timezone
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.token import JWTClient
from src.core.database import get_db
from src.models.session import Session
from src.models.user import User
from src.schemas.session_schemas import SessionSchema
from src.schemas.user_schemas import UserSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/sign-in")

T_Database = Annotated[AsyncSession, Depends(get_db)]


async def get_session(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: T_Database,
) -> SessionSchema:
    token_client = JWTClient()
    payload = token_client.decode_access_token(token)

    session_id = UUID(payload.sessionId)
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Session not found"
        )

    return SessionSchema.model_validate(session)


T_Session = Annotated[SessionSchema, Depends(get_session)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: T_Database,
) -> UserSchema:
    token_client = JWTClient()
    payload = token_client.decode_access_token(token)

    # we should check if the session is even valid first
    session = await db.execute(
        select(Session).where(Session.id == UUID(payload.sessionId))
    )
    session = session.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Session not found"
        )

    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Session expired"
        )

    user_id = UUID(payload.sub)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="User not found"
        )

    return UserSchema.model_validate(user)


T_CurrentUser = Annotated[UserSchema, Depends(get_current_user)]
