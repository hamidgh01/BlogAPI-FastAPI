from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Table, Column, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from . import Post


# 'posts_tags' association table to implement ManyToMany relationship
# between 'Posts' and 'Tags'.
# NOTE: PK here is the combination of "post_id" and "tag_id".
posts_tags = Table(
    "posts_tags",
    Base.metadata,
    Column(
        "post_id",
        ForeignKey("posts.ID", ondelete="CASCADE"),
        nullable=False
    ),
    Column(
        "tag_id",
        ForeignKey("tags.ID", ondelete="CASCADE"),
        nullable=False
    ),
    PrimaryKeyConstraint(
        "tag_id", "post_id",
        name="posts_tags_composite_pk"
    ),  # NOTE: this primary key is automatically UNIQUE
)


class Tag(Base):
    """
    Table/Model: Tag (tags)
    Fields:
        ID (PK), name
    Relations:
    _ N:N (Many to Many) with 'Post' -> Post.tags / Tag.posts
        (via posts_tags association table)
    """

    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )

    # N:N with Post ('posts_tags' association table)
    posts: Mapped[list[Post]] = relationship(
        "Post",
        secondary=posts_tags,
        back_populates="tags"
    )
