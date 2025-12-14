from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from sqlalchemy import insert, update, delete, and_

from src.models import Profile, Link
from src.core.exceptions import BadRequestException, NotFoundException

from .utils import handle_unexpected_db_error

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.schemas.profile import ProfileUpdate, LinkCreate, LinkUpdate


class ProfileCrud:
    """ CRUD operations for Profile model """

    @staticmethod
    @handle_unexpected_db_error("create profile")
    async def create(user_id: int, db: AsyncSession) -> None:
        """
        NOTE: this method isn't used independently in a special service. this
        method is used in `UserService.register_user`: after creating user-obj
        (`UserCrud.create`) a profile-obj is created too (`ProfileCrud.create`)
        """
        profile = Profile(user_id=user_id)
        db.add(profile)
        await db.commit()
        # await db.refresh(profile)
        # return profile

    @staticmethod
    @handle_unexpected_db_error("update profile")
    async def update(
        user_id: int, data: ProfileUpdate, db: AsyncSession
    ) -> Profile:
        data = data.model_dump(exclude_none=True)
        if not data:
            raise BadRequestException("Empty field values to update.")
        query = update(Profile).where(
            Profile.user_id == user_id
        ).values(**data).returning(Profile)
        result = await db.execute(query)
        await db.commit()
        updated_profile: Optional[Profile] = result.scalars().one_or_none()
        # if updated_profile is None:  # ToDo: handle it later
        return updated_profile

    # async def delete(...) -> None:
    # NOTE: no need to implement delete() method for ProfileCrud. because:
    # if a User-object would be deleted, its related Profile-object would
    # be deleted too (models/profile.py:line79 -> ondelete="CASCADE")

    @staticmethod
    async def retrieve_details(db: AsyncSession) -> Profile:
        pass

    @staticmethod
    async def retrieve_list(db: AsyncSession) -> list[Profile]:
        pass


class LinkCrud:
    """ CRUD operations for Link model """

    @staticmethod
    @handle_unexpected_db_error("create links")
    async def create(links: list[LinkCreate], db: AsyncSession) -> list[Link]:
        links = [link.model_dump() for link in links]
        for dictionary in links:
            dictionary["url"] = str(dictionary["url"])
        query = insert(Link).values(links).returning(Link)  # bulk insert
        result = await db.execute(query)
        await db.commit()
        created_links: list[Link] = result.scalars().all()
        return created_links

    @staticmethod
    @handle_unexpected_db_error("update link")
    async def update(
        user_id: int, pk: int, data: LinkUpdate, db: AsyncSession
    ) -> Link | None:
        data = data.model_dump(exclude_none=True)
        if len(data) <= 1:  # profile_id is required, so `len` at least = 1
            raise BadRequestException("Empty field values to update.")
        if data.get("url", None):
            data["url"] = str(data["url"])
        query = update(Link).where(
            and_(Link.ID == pk, Link.profile_id == user_id)
        ).values(**data).returning(Link)
        result = await db.execute(query)
        await db.commit()
        updated_link: Optional[Link] = result.scalars().one_or_none()
        return updated_link  # Link | None

    @staticmethod
    @handle_unexpected_db_error("delete link")
    async def delete(user_id: int, pk: int, db: AsyncSession) -> None:
        query = delete(Link).where(
            and_(Link.ID == pk, Link.profile_id == user_id)
        ).returning(Link.ID)
        result = await db.execute(query)
        await db.commit()
        if result.scalar_one_or_none() is None:
            raise NotFoundException(
                f"Requester(pk='{user_id}') is not owner of "
                f"any Link with pk='{pk}'"
            )

    @staticmethod
    async def retrieve_list(db: AsyncSession) -> list[Link]:
        pass
