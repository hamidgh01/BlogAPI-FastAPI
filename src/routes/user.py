"""
user-related routes
* both `UserService` and `AuthService` provide their services here
"""

from typing import Annotated

from fastapi import APIRouter, status, Depends, Request, Response, Path
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.utils import dependencies as deps
from src.core.security import jwt_bearer
from src.models import User
from src.schemas import user as user_sch, profile as profile_sch
from src.schemas.GENERAL import Message, Token
from src.services import UserService, AuthService


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    data: user_sch.CreateUserSchema,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    await UserService.register_user(data, db)
    return Message(message="User created successfully.")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    response: Response,
    data: user_sch.UserLoginRequestSchema,
    redis: Annotated[Redis, Depends(deps.get_redis)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> user_sch.LoginSuccessfulData:
    return await AuthService.login(request, response, data, redis, db)


@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
    redis: Annotated[Redis, Depends(deps.get_redis)]
) -> Message:
    await AuthService.logout(request, response, credentials, redis)
    return Message(message="Successfully logged out.")


@router.get("/renew-tokens", status_code=status.HTTP_200_OK)
async def renew_tokens(
    request: Request,  # <---------- is this route vulnerable against CSRF ???
    response: Response,
    redis: Annotated[Redis, Depends(deps.get_redis)]
) -> Token:
    return await AuthService.renew_tokens(request, response, redis)


@router.put("/user", status_code=status.HTTP_202_ACCEPTED)
async def update_user(
    data: user_sch.UpdateUserSchema,
    current_user: Annotated[User, Depends(deps.get_current_user_object)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> user_sch.UserOutSchema:
    return await UserService.update_user(current_user, data, db)


@router.put("/password", status_code=status.HTTP_202_ACCEPTED)
async def update_password(
    data: user_sch.UpdatePasswordSchema,
    current_user: Annotated[User, Depends(deps.get_current_user_object)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> Message:
    await UserService.update_password(current_user, data, db)
    return Message(message="Password updated successfully.")


# @router.put("/reset-password", status_code=status.HTTP_202_ACCEPTED)
# async def reset_password_by_email(): pass  # needs some routes and steps


@router.put("/profile", status_code=status.HTTP_202_ACCEPTED)
async def update_profile(
    data: profile_sch.UpdateProfileSchema,
    current_user_id: Annotated[User, Depends(deps.get_current_user_id)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> profile_sch.ProfileOutAfterUpdate:
    return await UserService.update_profile(current_user_id, data, db)


@router.post("/link", status_code=status.HTTP_201_CREATED)
async def add_link(
    data: list[profile_sch.CreateLinkSchema],
    current_user_id: Annotated[User, Depends(deps.get_current_user_id)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> list[profile_sch.LinkOut]:
    return await UserService.add_link(current_user_id, data, db)


@router.put("/link/{pk}", status_code=status.HTTP_202_ACCEPTED)
async def update_link(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of link")],
    data: profile_sch.UpdateLinkSchema,
    current_user_id: Annotated[User, Depends(deps.get_current_user_id)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
) -> profile_sch.LinkOut:
    return await UserService.update_link(current_user_id, pk, data, db)


@router.delete("/link/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    pk: Annotated[int, Path(..., gt=0, description="unique ID of link")],
    current_user_id: Annotated[User, Depends(deps.get_current_user_id)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    await UserService.delete_link(current_user_id, pk, db)
    # return Message(message="Link deleted successfully.")


# @router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     current_user: Annotated[User, Depends(deps.get_current_user_object)],
#     db: Annotated[AsyncSession, Depends(deps.get_db)]
# ):
#     await UserService.delete_user(current_user, db)
