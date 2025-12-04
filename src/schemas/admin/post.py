""" admin-specific 'Post' schemas """

from typing import Annotated, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models import PostStatus
from ..user import UserOut
from ..post import TagOut


class PostListOutForAdmin(BaseModel):
    ID: int
    title: str
    reading_time: Annotated[Optional[int], Field(
        None, description="Estimated reading time (seconds)"
    )]
    status: Annotated[PostStatus, Field(
        ...,
        description="Post status enum: "
                    "draft/published/rejected/deleted-by-author"
    )]
    is_private: bool
    created_at: datetime
    published_at: Optional[datetime] = None

    user: Annotated[UserOut, Field(
        ..., description="Contains 'username' and 'id' of related user"
    )]

    saved_by_viewer: Annotated[bool, Field(
        ...,
        description="indicates that the viewer (current user) "
                    "saved this post or not (true/false)"
    )]

    model_config = ConfigDict(from_attributes=True)


class PostDetailsOutForAdmin(PostListOutForAdmin):
    content: Optional[str] = None
    updated_at: datetime

    like_count: int
    comment_count: int
    tags: Optional[list[TagOut]] = None

    liked_by_viewer: Annotated[bool, Field(
        ...,
        description="indicates that the viewer (current user) "
                    "liked this post or not (true/false)"
    )]
