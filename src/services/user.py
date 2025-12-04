from __future__ import annotations
from typing import TYPE_CHECKING, Literal

from src.core.security import PasswordHandler
from src.core.exceptions import (
    InternalServerError,
    ForbiddenException,
    BadRequestException,
    NotFoundException
)
from src.crud import UserCrud, FollowCrud, ProfileCrud, LinkCrud
from src.schemas.user import (
    UserOut, SetPassword, FollowerOrFollowingListOut
)
from src.schemas.profile import ProfileOutAfterUpdate, LinkOut

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.models import User
    from src.schemas.user import (
        UserCreate,
        UserUpdate,
        UpdatePassword,
        FollowCreate,
        UnfollowOrRemoveFollowerSchema,
    )
    from src.schemas.profile import ProfileUpdate, LinkCreate, LinkUpdate


class UserService:
    """
    User and Profile services
    (interacts with `UserCrud`, `ProfileCrud` & `LinkCrud`)
    NOTE:
    _ the method `register_user()` creates both `User` and `Profile` object
    _ the method `delete_user()` deletes `User` (and then its related `Profile`
      would be deleted too)
    """

    @staticmethod
    async def register_user(data: UserCreate, db: AsyncSession) -> None:
        user = await UserCrud.create(data, db)
        try:
            await ProfileCrud.create(user_id=user.ID, db=db)
        except InternalServerError as err:
            await UserCrud.delete(user, db)
            msg = err.message + " created-user was deleted too."
            raise InternalServerError(msg) from err

    @staticmethod
    async def update_user(
        current_user: User, data: UserUpdate, db: AsyncSession
    ) -> UserOut:
        user = await UserCrud.update(current_user, data, db)
        return UserOut.model_validate(user)

    @staticmethod
    async def update_password(
        current_user: User, data: UpdatePassword, db: AsyncSession
    ) -> None:
        is_old_password_verified = PasswordHandler.verify_password(
            data.old_password, current_user.password
        )
        if not is_old_password_verified:
            raise BadRequestException("Old password is invalid.")
        data = SetPassword(**data.model_dump())
        await UserCrud.set_new_password(current_user, data, db)

    @staticmethod
    async def reset_password_by_email(
        data: SetPassword, db: AsyncSession
    ) -> None:
        pass  # ToDo: add later (need to implement email system)

    @staticmethod
    async def update_profile(
        current_user_id: int, data: ProfileUpdate, db: AsyncSession
    ) -> ProfileOutAfterUpdate:
        profile = await ProfileCrud.update(current_user_id, data, db)
        return ProfileOutAfterUpdate.model_validate(profile)

    @staticmethod
    async def add_link(
        current_user_id: int, data: list[LinkCreate], db: AsyncSession
    ) -> list[LinkOut]:
        if not data:
            return []  # ToDo: maybe change here
        if any(link_sch.profile_id != current_user_id for link_sch in data):
            raise ForbiddenException("Operation is not allowed!")
        updated_links = await LinkCrud.create(data, db)
        return [LinkOut.model_validate(link) for link in updated_links]

    @staticmethod
    async def update_link(
        current_user_id: int, pk: int, data: LinkUpdate, db: AsyncSession
    ) -> LinkOut:
        updated_link = await LinkCrud.update(current_user_id, pk, data, db)
        if updated_link is None:
            raise NotFoundException(
                f"Requester(pk='{current_user_id}') is not owner of "
                f"any Link with pk='{pk}'"
            )
        return LinkOut.model_validate(updated_link)

    @staticmethod
    async def delete_link(
        current_user_id: int, pk: int, db: AsyncSession
    ) -> None:
        await LinkCrud.delete(current_user_id, pk, db)

    @staticmethod
    async def follow(
        current_user_id: int, data: FollowCreate, db: AsyncSession
    ) -> Literal[1, 0]:
        if current_user_id == data.intended_user_id:
            raise BadRequestException("impossible request...!")
        return await FollowCrud.create(current_user_id, data, db)

    @staticmethod
    async def unfollow_or_remove(
        current_user_id: int,
        data: UnfollowOrRemoveFollowerSchema,
        db: AsyncSession
    ) -> Literal[1, 0]:
        if current_user_id == data.intended_user_id:
            raise BadRequestException("impossible request...!")
        return await FollowCrud.delete(current_user_id, data, db)

    @staticmethod
    async def get_followers_list(
        user_id: int, db: AsyncSession
    ) -> FollowerOrFollowingListOut:
        result = await FollowCrud.retrieve_followers(user_id, db)
        return FollowerOrFollowingListOut(users_list=list(
            map(lambda row: UserOut(ID=row[0], username=row[1]), result)
        ))

    @staticmethod
    async def get_followings_list(
        user_id: int, db: AsyncSession
    ) -> FollowerOrFollowingListOut:
        result = await FollowCrud.retrieve_followings(user_id, db)
        return FollowerOrFollowingListOut(users_list=list(
            map(lambda row: UserOut(ID=row[0], username=row[1]), result)
        ))

    # @staticmethod
    # async def delete_user(current_user: User, db: AsyncSession) -> None:
    #     await UserCrud.delete(current_user, db)
    #     # user's related Profile would be deleted too (ondelete="CASCADE")
    # there's a big bug here :)))) when db tries to delete User (fix it later)
