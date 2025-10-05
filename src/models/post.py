from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum as PythonEnum
from datetime import datetime

from sqlalchemy import (
    String, Text, SmallInteger, BigInteger, DateTime,
    ForeignKey, Enum as SqlEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from ._mixins import CreatedAtFieldMixin, UpdateAtFieldMixin
from .tag import posts_tags
from .lists import saved_posts
from .interactions import post_likes

if TYPE_CHECKING:
    from . import User, Tag, Comment, List, ReportOnPost


class PostStatus(PythonEnum):
    DR = "draft"
    PB = "published"
    RJ = "Rejected"
    DL = "Deleted-By-Author"


class Post(Base, CreatedAtFieldMixin, UpdateAtFieldMixin):
    """
    Table/Model: Post (posts)
    Fields:
        ID (PK), title, slug, content, reading_time, status,
        created_at, published_at, updated_at, user_id (FK)

    Points/Notes:
        _ 'slug' is generated via 'title' [calculated_field]
        _ post_details is fetched using 'ID' (slug usage: making semantic url)
        _ 'reading_time' is generated via 'content' [calculated_field]

    Relations:
    _ N:1 (Many to One) with 'User' -> Post.author / User.posts
    _ N:N (Many to Many) with 'Tag' -> Post.tags / Tag.posts
      (via 'posts_tags' association table)
    _ 1:N (One to Many) with 'Comment' -> Post.comments / Comment.post
    _ N:N (Many to Many) with 'List' -> Post.lists / List.posts
      (via 'saved_posts' association table)
    _ 1:N (One to Many) with 'ReportOnPost'
      ->  Post.received_reports / ReportOnPost.reported_post
    _ N:N (Many to Many) with 'User' (like-system)
      -> Post.likers / User.liked_posts (via 'post_likes' association table)
    """

    __tablename__ = "posts"

    # ID (defined in Base)
    title: Mapped[str] = mapped_column(
        String(length=250),
        nullable=False,
        index=True
    )
    slug: Mapped[str] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    reading_time: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[PostStatus] = mapped_column(
        SqlEnum(PostStatus, name="post_status_enum"),
        default=PostStatus.DR, nullable=False
    )
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # ToDo: I'll possibly index this column

    # N:1 with User (backref: author)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.ID",
            name="fk_users_posts",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )
    # NOTE: because of using 'backref="author"' in referenced table 'User',
    # you don't need to define 'relationship(...)' here.

    # N:N with Tag ('posts_tags' association table)
    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary=posts_tags,
        back_populates="posts"
    )
    # 1:N with Comment
    comments: Mapped[list[Comment]] = relationship(
        "Comment", backref="post"
    )
    # N:N with List ('saved_posts' association table)
    lists: Mapped[list[List]] = relationship(
        "List",
        secondary=saved_posts,
        back_populates="posts"
    )
    # N:N with User (like-system) ('post_likes' association table)
    likers: Mapped[list[User]] = relationship(
        "User",
        secondary=post_likes,
        back_populates="liked_posts"
    )
    # 1:N with ReportOnPost
    received_reports: Mapped[list[ReportOnPost]] = relationship(
        "ReportOnPost", backref="reported_post"
    )

    # ToDo: if for a user: is_active=False --> his posts should be hidden too.
