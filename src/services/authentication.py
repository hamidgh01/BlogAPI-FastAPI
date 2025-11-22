from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timezone, timedelta

from src.core.config import settings
from src.core.exceptions import UnauthorizedException
from src.auth import JWTHandler, TokenRevocation
from src.crud import UserCrud
from src.schemas.user import LoginSuccessfulData, UserOutSchema
from src.schemas.GENERAL import Token

if TYPE_CHECKING:
    from fastapi import Request, Response
    from fastapi.security import HTTPAuthorizationCredentials
    from sqlalchemy.ext.asyncio import AsyncSession
    from redis.asyncio import Redis

    from src.schemas.user import UserLoginRequestSchema


class AuthService:
    """ Authentication services """

    @staticmethod
    async def login(
        response: Response, data: UserLoginRequestSchema, db: AsyncSession
    ) -> LoginSuccessfulData:
        user = await UserCrud.verify_user_for_login(data, db)
        if user is None:
            raise UnauthorizedException("Invalid username, email or password")

        user = UserOutSchema(ID=user.ID, username=user.username)
        access_token = JWTHandler.generate_token(user.ID, "access")
        refresh_token = JWTHandler.generate_token(user.ID, "refresh")

        AuthService._add_refresh_token_cookie(response, refresh_token)
        token = Token(access_token=access_token)
        return LoginSuccessfulData(user=user, token=token)

    @staticmethod
    async def logout(
        request: Request,
        response: Response,
        credentials: HTTPAuthorizationCredentials,
        redis: Redis
    ) -> None:
        access_token = credentials.credentials
        refresh_token = request.cookies.get("X-Auth-Token", None)
        if refresh_token is None:
            raise UnauthorizedException("Token Not provided.")

        refresh_token_payload = await JWTHandler.get_token_payload(
            refresh_token, "refresh", redis
        )
        access_token_payload = await JWTHandler.get_token_payload(
            access_token, "access", redis
        )
        await TokenRevocation.put_in_blacklist(refresh_token_payload, redis)
        await TokenRevocation.put_in_blacklist(access_token_payload, redis)
        response.delete_cookie("X-Auth-Token")

    @staticmethod
    async def renew_tokens(
        request: Request, response: Response, redis: Redis
    ) -> Token:
        refresh_token = request.cookies.get("X-Auth-Token", None)
        if refresh_token is None:
            raise UnauthorizedException("Token Not provided.")

        refresh_token_payload = await JWTHandler.get_token_payload(
            refresh_token, "refresh", redis
        )
        user_id = refresh_token_payload.get("user_id")
        new_access_token = JWTHandler.generate_token(user_id, "access")
        new_refresh_token = JWTHandler.generate_token(user_id, "refresh")

        # NOTE: `old-refresh-token` must be blacklisted *after* calling
        # JWTHandler.get_token_payload (actually calling JWTHandler._decode)
        # because: to get the `payload` using JWTHandler.get_token_payload, its
        # blacklisting statement is checked and -> if blacklisted: raises error
        await TokenRevocation.put_in_blacklist(refresh_token_payload, redis)

        AuthService._add_refresh_token_cookie(response, new_refresh_token)
        return Token(access_token=new_access_token)

    @staticmethod
    def _add_refresh_token_cookie(response: Response, token: str) -> None:
        utc_now = datetime.now(timezone.utc)
        expires_at = utc_now + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        response.set_cookie(
            key="X-Auth-Token",
            value=token,
            expires=expires_at,
            secure=True,
            httponly=True,
            samesite="strict"
        )
