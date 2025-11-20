from __future__ import annotations
from typing import TYPE_CHECKING

from src.crud import UserCrud, ProfileCrud, LinkCrud
from src.core.security import PasswordHandler
from src.core.exceptions import (
    InternalServerError,
    ForbiddenException,
    BadRequestException,
    NotFoundException
)
from src.schemas.user import SetPasswordSchema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.models import User, Profile, Link
    from src.schemas.user import (
        CreateUserSchema, UpdateUserSchema, UpdatePasswordSchema
    )
    from src.schemas.profile import (
        UpdateProfileSchema, CreateLinkSchema, UpdateLinkSchema
    )


class UserService:
    """
    User and Profile services
    (interacts with `UserCrud`, `ProfileCrud` & `LinkCrud`)

    register_user   : create both User and Profile object
    delete_user     : delete User (its related Profile'd be deleted too)
    update_user             : obvious ;)
    update_password         : ...
    reset_password_by_email : ...
    update_profile          : ...
    add_link                : ...
    update_link             : ...
    delete_link             : ...
    """

    @staticmethod
    async def register_user(data: CreateUserSchema, db: AsyncSession) -> None:
        user = await UserCrud.create(data, db)
        try:
            await ProfileCrud.create(user_id=user.ID, db=db)
        except InternalServerError as err:
            await UserCrud.delete(user, db)
            msg = err.message + " created-user was deleted too."
            raise InternalServerError(msg) from err

    @staticmethod
    async def update_user(
        current_user: User, data: UpdateUserSchema, db: AsyncSession
    ) -> User:
        return await UserCrud.update(current_user, data, db)

    @staticmethod
    async def update_password(
        current_user: User, data: UpdatePasswordSchema, db: AsyncSession
    ) -> None:
        is_old_password_verified = PasswordHandler.verify_password(
            data.old_password, current_user.password
        )
        if not is_old_password_verified:
            raise BadRequestException("Old password is invalid.")
        data = SetPasswordSchema(**data.model_dump())
        await UserCrud.set_new_password(current_user, data, db)

    @staticmethod
    async def reset_password_by_email(
        data: SetPasswordSchema, db: AsyncSession
    ) -> None:
        pass  # ToDo: add later (need to implement email system)

    @staticmethod
    async def update_profile(
        current_user_id: int, data: UpdateProfileSchema, db: AsyncSession
    ) -> Profile:
        return await ProfileCrud.update(current_user_id, data, db)

    @staticmethod
    async def add_link(
        current_user_id: int, data: list[CreateLinkSchema], db: AsyncSession
    ) -> list[Link]:
        if not data:
            return []  # ToDo: maybe change here
        if any(link_sch.profile_id != current_user_id for link_sch in data):
            raise ForbiddenException("Operation is not allowed!")
        return await LinkCrud.create(data, db)

    @staticmethod
    async def update_link(
        current_user_id: int, pk: int, data: UpdateLinkSchema, db: AsyncSession
    ) -> Link:
        updated_link = await LinkCrud.update(current_user_id, pk, data, db)
        if updated_link is None:
            raise NotFoundException(
                f"Requester(pk='{current_user_id}') is not owner of "
                f"any Link with pk='{pk}'"
            )

    @staticmethod
    async def delete_link(
        current_user_id: int, pk: int, db: AsyncSession
    ) -> None:
        await LinkCrud.delete(current_user_id, pk, db)

    # @staticmethod
    # async def delete_user(current_user: User, db: AsyncSession) -> None:
    #     await UserCrud.delete(current_user, db)
    #     # user's related Profile would be deleted too (ondelete="CASCADE")
    # there's a big bug here :)))) when db tries to delete User (fix it later)
