from enum import Enum as PythonEnum
from datetime import datetime

from sqlalchemy import (
    String, Text, SmallInteger, BigInteger, DateTime,
    ForeignKey, func, Enum as SqlEnum
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PostStatus(PythonEnum):
    DR = "draft"
    PB = "published"
    RJ = "Rejected"
    DL = "Deleted-By-Author"


class Post(Base):
    """
    Table/Model: Post (posts)
    Fields:
        id, title, slug, content, reading_time,
        status, created_at, published_at, updated_at

    Points/Notes:
        _ 'slug' is generated via 'title' [calculated_field]
        _ post_details is fetched using 'id' (slug usage: making semantic url)
        _ 'reading_time' is generated via 'content' [calculated_field]

    Relations:
        _ N:1 (Many to One) with 'User' -> Post.author / User.posts
    """

    __tablename__ = "posts"

    # id (defined in Base)
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )

    # N:1 with User (backref: author)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", name="fk_users_posts", ondelete="CASCADE"),
        nullable=False
    )
    # NOTE: because of using 'backref="author"' in referenced table 'User',
    # you don't need to define 'relationship(...)'

    # ToDo: if for a user: is_active=False --> his posts should be hidden too.
