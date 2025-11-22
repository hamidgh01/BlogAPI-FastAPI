from typing import AsyncGenerator, Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.core.database import AsyncSessionLocal
from src.core.security import jwt_bearer
from src.auth import JWTHandler
from src.models.user import User
from src.crud.user import UserCrud
from src.core.exceptions import (
    NotFoundException, UnauthorizedException, ForbiddenException
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db_session:
        yield db_session


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> int:
    access_token = credentials.credentials
    payload = await JWTHandler.get_token_payload(access_token, "access", redis)
    user_id = payload.get("user_id")
    return user_id


async def get_current_user_object(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    try:
        # user = ... (cache users in redis and get from redis)
        user = await UserCrud.get_by_id(user_id, db)
    except NotFoundException as err:
        raise UnauthorizedException(err.message) from err

    if not user.is_active:
        raise ForbiddenException(f"The user {user.username!r} is suspended.")

    return user


async def authenticate_admin(
    user: Annotated[User, Depends(get_current_user_object)]
) -> User:
    if user.is_superuser:
        return user
    raise ForbiddenException("Forbidden access to endpoint.")
