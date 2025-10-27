from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Optional, Type, TypeVar
from uuid import UUID

import jwt
from fastapi import HTTPException

from src.core.config import jwt_settings
from src.core.constants import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from src.schemas.auth_schemas import AccessToken, RefreshToken, TokenBase

T = TypeVar("T", bound=TokenBase)


class JWTClient:
    def __init__(self):
        self.secret_key = jwt_settings.secret_key

    def create_access_token(
        self,
        user_id: UUID,
        session_id: UUID,
        roles: list[str],
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
            "roles": roles,
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

    def decode_token(self, token: str, token_class: Type[T]) -> T:
        """Generic method to decode JWT tokens into AccessToken or RefreshToken"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return token_class(**payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token"
            )

    def decode_access_token(self, token: str) -> AccessToken:
        """Decode an access token"""
        return self.decode_token(token, AccessToken)

    def decode_refresh_token(self, token: str) -> RefreshToken:
        """Decode a refresh token"""
        return self.decode_token(token, RefreshToken)
