from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from src.core.exceptions import (
    NotFoundException, BadRequestException, InternalServerError
)
from src.crud import PostCrud, TagCrud, PostTagAssociation, UserCrud
from src.models import PostStatus
from src.schemas.post import PostOut, PostDetailsOut, TagOut, PostUpdateStatus
from src.schemas.user import UserOut

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.models import User, Post, Tag
    from src.schemas.post import (
        TagsIn,
        PostCreate,
        PostUpdate,
        ChangePostPrivacy
    )


class PostService:
    """ Post and Tag services """

    @staticmethod
    async def add_draft_post(
        current_user_id: int,
        data: PostCreate,
        db: AsyncSession
    ) -> tuple[PostOut, Optional[list[TagOut]]]:
        tags = {tag.lower() for tag in data.tags} if data.tags else None
        data = data.model_dump(exclude={"tags"}, exclude_none=True)
        post = await PostCrud.create(current_user_id, data, db)
        draft_out = PostOut.model_validate(post)
        if not tags:
            return draft_out, None
        try:
            # 1: create non-existing tags and return + get existing tags
            tag_objects = await TagCrud.get_or_create_tags_list(tags, db)
            # 2: associate all tags with post
            await PostTagAssociation.associate(post.ID, tag_objects, db)
            tags_out = [
                TagOut.model_validate(tag) for tag in tag_objects
            ] if tag_objects else None
        except InternalServerError:
            tags_out = None
            # ToDo: set an operation to send a message like: failed to
            # assign tags / and log the reason (err.message)

        return draft_out, tags_out

    @staticmethod
    async def publish(
        current_user_id: int, pk: int, db: AsyncSession
    ) -> PostDetailsOut:
        post = await PostCrud.publish_draft(current_user_id, pk, db)
        if post is None:
            raise NotFoundException("Invalid request!")
            # due to: ownership / trying to republish / published deleted post

        author: User = await UserCrud.get_by_id(post.user_id, db)
        tag_objects = await TagCrud.get_tags_of_a_post(post.ID, db)

        return PostService._build_post_details_out(
            post, author, tag_objects, True
        )

    @staticmethod
    async def update_post_fields(
        current_user_id: int,
        pk: int,
        data: PostUpdate,
        db: AsyncSession
    ) -> PostOut:
        data = data.model_dump(exclude_none=True)
        if not data:
            raise BadRequestException("Empty field values to update.")

        post = await PostCrud.update(current_user_id, pk, data, db)
        if post is None:
            raise NotFoundException(
                f"Requester(pk='{current_user_id}') is not owner of "
                f"any Post with pk='{pk}'"
            )

        return PostOut.model_validate(post)

    @staticmethod
    async def update_tags_of_post(
        current_user_id: int, post_id: int, tags: TagsIn, db: AsyncSession,
    ) -> list[TagOut]:
        tags = {tag.lower() for tag in tags.tags}
        if not tags:
            raise BadRequestException("Empty field values to update.")

        async with db.begin():
            post = await PostCrud.get_by_id(post_id, db)
            if not post.user_id == current_user_id:  # check ownership
                raise NotFoundException(
                    f"Requester(pk='{current_user_id}') is not owner of "
                    f"any Post with pk='{post_id}'"
                )
            # check status
            if post.status == PostStatus.RJ or post.status == PostStatus.DL:
                raise BadRequestException("invalid operation.")
                # reason: trying to update tags for DELETED or REJECTED post
            try:
                # 1: dissociate previous tags (if there is any)
                await PostTagAssociation.dissociate(post_id, db)
                # 2: create non-existing tags and return + get existing tags
                tag_objects = await TagCrud.get_or_create_tags_list(tags, db)
                # 3: associate all tags with post
                await PostTagAssociation.associate(post_id, tag_objects, db)
            except InternalServerError as err:
                raise InternalServerError(
                    "Failed to update tags (nothing changed)"
                ) from err
                # ToDo; log the reason (err.message)

        return [TagOut.model_validate(tag) for tag in tag_objects]

    @staticmethod
    async def change_privacy_stmt(
        current_user_id: int,
        pk: int,
        data: ChangePostPrivacy,
        db: AsyncSession
    ) -> bool:
        privacy_statement = await PostCrud.update_privacy(
            current_user_id, pk, data.model_dump(), db
        )
        if privacy_statement is None:
            raise NotFoundException(
                f"Requester(pk='{current_user_id}') is not owner of "
                f"any Post with pk='{pk}'"
            )
        return privacy_statement

    @staticmethod  # NOTE: admin specific service
    async def reject_post(pk: int, db: AsyncSession) -> None:
        data = PostUpdateStatus(status=PostStatus.RJ)
        result = await PostCrud.update_status(
            pk, data, db, operation_is_requested_by="admin"
        )
        if result is None:
            raise BadRequestException(
                "invalid operation. only 'published' posts can be rejected!"
            )

    @staticmethod  # NOTE: admin specific service
    async def publish_rejected_post(pk: int, db: AsyncSession) -> None:
        data = PostUpdateStatus(status=PostStatus.PB)
        result = await PostCrud.update_status(pk, data, db, "admin")
        if result is None:
            raise BadRequestException(
                "invalid operation. only 'rejected' posts can be republished!"
            )

    @staticmethod
    async def delete_post_at_user_request(
        current_user_id: int, pk: int, db: AsyncSession
    ) -> None:
        data = PostUpdateStatus(status=PostStatus.DL)
        result = await PostCrud.update_status(
            pk, data, db, "author", current_user_id
        )
        if result is None:
            raise NotFoundException(
                f"Requester(pk='{current_user_id}') is not owner of "
                f"any Post with pk='{pk}'"
            )

    @staticmethod  # NOTE: admin specific service
    async def delete_post(pk: int, db: AsyncSession) -> None:
        await PostCrud.delete(pk, db)

    # ----------------------------------------------------------------

    @staticmethod
    def _build_post_details_out(
        post: Post,
        author: User,
        tags: Optional[list[Tag]] = None,
        is_first_published: bool = False
    ) -> PostDetailsOut:
        tags_out = [TagOut.model_validate(t) for t in tags] if tags else None
        user_out = UserOut.model_validate(author)
        if is_first_published:
            cm_count, like_count, is_liked, is_saved = 0, 0, False, False
        else:
            cm_count = 0  # ToDo: implement later
            like_count = 0  # ToDo: implement later
            is_liked = False  # ToDo: implement later
            is_saved = False  # ToDo: implement later

        return PostDetailsOut(
            ID=post.ID,
            title=post.title,
            content=post.content,
            reading_time=post.reading_time,
            created_at=post.created_at,
            updated_at=post.updated_at,
            published_at=post.published_at,
            tags=tags_out,
            user=user_out,
            comment_count=cm_count,
            like_count=like_count,
            liked_by_viewer=is_liked,
            saved_by_viewer=is_saved
        )
