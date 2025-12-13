from __future__ import annotations
from typing import TYPE_CHECKING

from src.core.exceptions import NotFoundException, BadRequestException
from src.crud.comment import CommentCrud
from src.models import CommentStatus
from src.schemas.comment import CommentOut

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    """ Comment services """

    @staticmethod
    async def add_comment(
        current_user_id: int,
        data: CommentCreate,
        db: AsyncSession
    ) -> CommentOut:
        data_dict = data.model_dump(exclude={"parent_id", "parent_type"})
        match data.parent_type:
            case "post":
                data_dict.update({"post_parent_id": data.parent_id})
            case "comment":
                data_dict.update({"comment_parent_id": data.parent_id})
        # to implement later (maybe):
        # limit commenting on DR/RJ/DL posts and DL/HD comments
        comment = await CommentCrud.create(current_user_id, data_dict, db)
        return CommentOut.model_validate(comment)

    @staticmethod
    async def update_comment(
        current_user_id: int,
        pk: int,
        data: CommentUpdate,
        db: AsyncSession
    ) -> CommentOut:
        comment = await CommentCrud.update_content(
            current_user_id, pk, data.model_dump(), db
        )
        if comment is None:
            raise NotFoundException(
                f"Requester(pk='{current_user_id}') is not owner of "
                f"any Comment with pk='{pk}'"
            )

        return CommentOut.model_validate(comment)

    @staticmethod  # NOTE: admin specific service
    async def hide_comment(pk: int, db: AsyncSession) -> None:
        data = {"status": CommentStatus.HD}
        result = await CommentCrud.update_status(
            pk, data, db, operation_is_requested_by="admin"
        )
        if result is None:
            raise BadRequestException(
                "invalid operation. only 'published' comments can be hidden!"
            )

    @staticmethod  # NOTE: admin specific service
    async def unhide_comment(pk: int, db: AsyncSession) -> None:
        data = {"status": CommentStatus.PB}
        result = await CommentCrud.update_status(
            pk, data, db, "admin"
        )
        if result is None:
            raise BadRequestException(
                "invalid operation. only 'hidden' comments can be unhidden!"
            )

    @staticmethod
    async def delete_comment_at_user_request(
        current_user_id: int, pk: int, db: AsyncSession
    ) -> None:
        data = {"status": CommentStatus.DL}
        result = await CommentCrud.update_status(
            pk, data, db, "commenter", current_user_id
        )
        if result is None:
            raise BadRequestException(
                f"Requester(pk='{current_user_id}') is not owner of "
                f"any Post with pk='{pk}'"
            )

    @staticmethod  # NOTE: admin specific service
    async def delete_comment(pk: int, db: AsyncSession) -> None:
        await CommentCrud.delete(pk, db)
