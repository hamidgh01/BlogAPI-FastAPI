from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal
from datetime import datetime

from sqlalchemy import select, insert, update, delete, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from src.models import Post, PostStatus, Tag, posts_tags
from src.core.exceptions import NotFoundException, InternalServerError

from .utils import handle_unexpected_db_error


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.schemas.post import PostUpdateStatus


class PostCrud:
    """ CRUD operations for Post model """

    @staticmethod
    async def create(
        current_user_id: int, data: dict, db: AsyncSession
    ) -> Post:
        query = insert(Post).values(
            **data, user_id=current_user_id
        ).returning(Post)
        try:
            result = await db.execute(query)
            await db.commit()
            return result.scalar()
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "create `Post`", err)

    @staticmethod
    async def publish_draft(
        current_user_id: int, pk: int, db: AsyncSession
    ) -> Post | None:
        """ change `status` to 'PB' & initialize `published_at` """
        now_ = datetime.now()
        query = update(Post).where(and_(
            Post.ID == pk,
            Post.user_id == current_user_id,
            Post.status == PostStatus.DR  # avoid repetitive publish-requests!
        )).values(status=PostStatus.PB, published_at=now_).returning(Post)
        try:
            result = await db.execute(query)
            await db.commit()
            post: Optional[Post] = result.scalars().one_or_none()
            return post

        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "publish the draft", err)

    @staticmethod
    async def update(
        current_user_id: int, pk: int, data: dict, db: AsyncSession
    ) -> Post | None:
        try:
            query = update(Post).where(and_(
                Post.ID == pk,
                Post.user_id == current_user_id,
                Post.status.in_({PostStatus.PB, PostStatus.DR})
            )).values(**data).returning(Post)
            result = await db.execute(query)
            await db.commit()
            post: Optional[Post] = result.scalars().one_or_none()
            return post

        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "update `Post`", err)

    @staticmethod
    async def update_privacy(
        current_user_id: int, pk: int, data: dict, db: AsyncSession
    ) -> bool | None:
        query = update(Post).where(and_(
            Post.ID == pk,
            Post.user_id == current_user_id,
            Post.status.in_({PostStatus.PB, PostStatus.DR})
        )).values(**data).returning(Post.is_private)
        try:
            result = await db.execute(query)
            await db.commit()
            privacy_statement: Optional[bool] = result.scalar_one_or_none()
            return privacy_statement
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "update post's privacy", err)

    @staticmethod
    async def update_status(
        pk: int,
        data: PostUpdateStatus,
        db: AsyncSession,
        operation_is_requested_by: Literal["admin", "author"],
        current_user_id: Optional[int] = None
    ) -> PostStatus | None:
        match operation_is_requested_by, data.status:
            case "admin", PostStatus.RJ:  # reject_post
                and_clause = and_(Post.ID == pk, Post.status == PostStatus.PB)
            case "admin", PostStatus.PB:  # publish_rejected_post
                and_clause = and_(Post.ID == pk, Post.status == PostStatus.RJ)
            case "author", PostStatus.DL:  # delete_post_at_user_request
                and_clause = and_(
                    Post.ID == pk,
                    Post.user_id == current_user_id,  # check ownership
                    Post.status.in_({PostStatus.PB, PostStatus.DR})
                )
            case _:
                raise InternalServerError(
                    "there's a server problem for this service."
                )
                # log here -> badly designed service

        query = update(Post).where(
            and_clause
        ).values(**data.model_dump()).returning(Post.status)
        try:
            result = await db.execute(query)
            await db.commit()
            status: Optional[PostStatus] = result.scalar_one_or_none()
            return status

        except SQLAlchemyError as err:
            if operation_is_requested_by == "admin":
                handle_unexpected_db_error(db, "update post's status", err)
            else:  # operation_is_requested_by "author"
                handle_unexpected_db_error(db, "delete post", err)

    @staticmethod  # NOTE: only "admin" access here
    async def delete(pk: int, db: AsyncSession) -> None:
        query = delete(Post).where(Post.ID == pk).returning(Post.ID)
        result = await db.execute(query)
        await db.commit()
        if result.scalar_one_or_none() is None:
            raise NotFoundException(f"Post(ID={pk}) is not found!")

    @staticmethod
    async def get_by_id(pk: int, db: AsyncSession) -> Post:
        post = await db.get(Post, pk)
        if post is None:
            raise NotFoundException(f"Post(ID={pk}) is not found!")
        return post


class TagCrud:
    """
    CRUD operations for Tag model
    NOTE: ... (no delete and update)
    """

    @staticmethod
    async def get_or_create_tags_list(
        tags: set[str], db: AsyncSession
    ) -> list[Tag]:
        try:
            rows = [{"name": name} for name in tags]
            q = pg_insert(Tag).values(rows).returning(Tag)  # bulk insert
            q = q.on_conflict_do_nothing(index_elements=["name"])
            result = await db.execute(q)
            await db.flush()

            created_tags: list[Tag] = result.scalars().all()
            created_tag_names: set[str] = {t.name for t in created_tags}

            # exists before, and not inserted (not returned) in previous step
            previously_existing_names: set[str] = tags - created_tag_names
            prev_existing_tags: list[Tag] = []
            if previously_existing_names:
                q = select(Tag).where(Tag.name.in_(previously_existing_names))
                result = await db.execute(q)
                prev_existing_tags: list[Tag] = result.scalars().all()

            all_tags: list[Tag] = created_tags + prev_existing_tags
            return all_tags

        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "get or create tags", err)

    @staticmethod
    async def get_tags_of_a_post(post_id: int, db: AsyncSession) -> list[Tag]:
        query = select(Tag).join(
            posts_tags, posts_tags.c.tag_id == Tag.ID
        ).where(posts_tags.c.post_id == post_id)
        try:
            tags: list[Tag] = (await db.execute(query)).scalars().all()
            return tags
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(
                db, f"retrieve tags of post(pk={post_id})", err
            )


class PostTagAssociation:
    """ CRUD operations for posts_tags association table """

    @staticmethod
    async def associate(
        post_id: int, tags: list[Tag], db: AsyncSession
    ) -> None:
        rows = [{"post_id": post_id, "tag_id": tag.ID} for tag in tags]
        q = pg_insert(posts_tags).values(rows)
        q = q.on_conflict_do_nothing(index_elements=["post_id", "tag_id"])
        try:
            await db.execute(q)
            await db.commit()
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "associate post-tags", err)

    @staticmethod
    async def dissociate(post_id: int, db: AsyncSession) -> None:
        query = delete(posts_tags).where(posts_tags.c.post_id == post_id)
        try:
            await db.execute(query)
            await db.flush()
        except SQLAlchemyError as err:
            await handle_unexpected_db_error(db, "dissociate post-tags", err)
