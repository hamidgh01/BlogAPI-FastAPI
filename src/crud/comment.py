from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal

from sqlalchemy import insert, update, delete, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.models import Comment, CommentStatus
from src.core.exceptions import (
    NotFoundException, InternalServerError, BadRequestException
)

from .utils import handle_unexpected_db_error

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class CommentCrud:
    """ CRUD operations for Comment model """

    @staticmethod
    async def create(
        current_user_id: int, data: dict, db: AsyncSession
    ) -> Comment:
        try:
            query = insert(Comment).values(
                **data, user_id=current_user_id
            ).returning(Comment)
            result = await db.execute(query)
            await db.commit()
            comment: Comment = result.scalar()
            return comment
        except IntegrityError as err:
            if 'constraint "fk_comments_reply_comments"' in str(err.orig):
                raise BadRequestException(
                    f"there's no comment with pk="
                    f"{data.get("comment_parent_id")} (as parent)"
                )
            elif 'constraint "fk_posts_comments"' in str(err.orig):
                raise BadRequestException(
                    f"there's no post with pk="
                    f"{data.get("post_parent_id")} (as parent)"
                )
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "create `Comment`", err)

    @staticmethod
    async def update_content(
        current_user_id: int, pk: int, data: dict, db: AsyncSession
    ) -> Comment | None:
        try:
            query = update(Comment).where(and_(
                Comment.ID == pk,
                Comment.user_id == current_user_id,
                Comment.status == CommentStatus.PB
            )).values(**data).returning(Comment)
            result = await db.execute(query)
            await db.commit()
            comment: Optional[Comment] = result.scalars().one_or_none()
            return comment
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "update `Comment`", err)

    @staticmethod
    async def update_status(
        pk: int,
        data: dict,
        db: AsyncSession,
        operation_is_requested_by: Literal["admin", "commenter"],
        current_user_id: Optional[int] = None
    ) -> Comment | None:
        """ this Schema is used when:
        _ admin 'hides' a comment  -> "Hidden-by-Admin"
        _ admin 'unhide' a comment  -> "published"
        _ commenter 'deletes' his/her comment  -> "Deleted-By-Commenter" """

        match operation_is_requested_by, data.get("status", None):
            case "admin", CommentStatus.HD:  # hide_comment
                and_clause = and_(
                    Comment.ID == pk, Comment.status == CommentStatus.PB
                )
            case "admin", CommentStatus.PB:  # unhide_comment
                and_clause = and_(
                    Comment.ID == pk, Comment.status == CommentStatus.HD
                )
            case "commenter", CommentStatus.DL:  # delete_comment_at_user_req
                and_clause = and_(
                    Comment.ID == pk,
                    Comment.user_id == current_user_id,  # check ownership
                    Comment.status == CommentStatus.PB
                )
            case _:
                raise InternalServerError(
                    "there's a server problem for this service."
                )
                # log here -> badly designed service

        query = update(Comment).where(
            and_clause
        ).values(**data).returning(Comment.status)
        try:
            result = await db.execute(query)
            await db.commit()
            status: Optional[CommentStatus] = result.scalar_one_or_none()
            return status

        except SQLAlchemyError as err:
            if operation_is_requested_by == "admin":
                handle_unexpected_db_error(db, "update comments's status", err)
            else:  # operation_is_requested_by "commenter"
                handle_unexpected_db_error(db, "delete comments", err)

    @staticmethod  # NOTE: only "admin" access here
    async def delete(pk: int, db: AsyncSession) -> None:
        query = delete(Comment).where(Comment.ID == pk).returning(Comment.ID)
        result = await db.execute(query)
        await db.commit()
        if result.scalar_one_or_none() is None:
            raise NotFoundException(f"Comment(ID={pk}) is not found!")
