"""
Global dependencies
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.clients.token import JWTClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/sign-in")

T_Database = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    token_client = JWTClient()
    token = token_client.decode_token(token=token)
    user_id = token["sub"]
    return {"user_id": user_id}


T_CurrentUser = Annotated[dict, Depends(get_current_user)]
