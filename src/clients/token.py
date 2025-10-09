from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import jwt
from fastapi import HTTPException

from src.core.config import jwt_settings
from src.models.session import SessionRoleEnum

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


class JWTClient:
    def __init__(self):
        self.secret_key = jwt_settings.secret_key

    def create_access_token(
        self,
        user_id: UUID,
        session_id: UUID,
        role: SessionRoleEnum,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token with session ID embedded"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )

        payload = {
            "sub": str(user_id),
            "sessionId": str(session_id),
            "role": role.value,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token

    def create_refresh_token(
        self, user_id: UUID, session_id: UUID, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )

        payload = {
            "sub": str(user_id),
            "sessionId": str(session_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token

    def decode_token(self, token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["H256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token"
            )
