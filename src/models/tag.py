from datetime import datetime

from sqlalchemy import (
    String, DateTime, ForeignKey, func,
    Table, Column, PrimaryKeyConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# 'posts_tags' association table to implement ManyToMany relationship
# between 'Posts' and 'Tags'.
# NOTE: PK here is the combination of "post_id" and "tag_id".
posts_tags = Table(
    "posts_tags",
    Base.metadata,
    Column(
        "post_id",
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
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
        id (PK), name, created_at
    Relations:
        _ N:N (Many to Many) with 'Post' -> Post.tags / Tag.posts
          (via posts_tags association table)
    """

    __tablename__ = "tags"

    # id (defined in Base)
    name: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # N:N with Post
    posts = relationship(
        "Post",
        secondary=posts_tags,
        back_populates="tags"
    )
