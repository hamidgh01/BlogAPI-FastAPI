from typing import Self
from enum import Enum as PythonEnum

from sqlalchemy import BigInteger, String, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from ._mixins import CreatedAtFieldMixin, UpdateAtFieldMixin


class CommentStatus(PythonEnum):
    PB = "published"
    HD = "Hidden-by-Admin"
    DL = "Deleted-By-Commenter"


class Comment(Base, CreatedAtFieldMixin, UpdateAtFieldMixin):
    """
    Table/Model: Comment (comments)
    Fields:
        ID (PK), content, created_at, updated_at, status,
        post_id (FK), user_id (FK), comment_parent_id (Self-Referenced)

    Points/Notes:
        parent of a comment can be another 'comment' or a 'post'.
        so for a comment-object:
        if parent is a 'post' --> comment_parent_id will be NULL
        if parent is another 'comment' --> post_parent_id will be NULL
        ('nullable=True' in comment_parent_id and post_parent_id)

    Relations:
        _ N:1 (Many to One) with 'User' -> Comment.commenter / User.comments
        _ N:1 (Many to One) with 'Post' -> Comment.post / Post.comments
        _ Self-Referenced -> Comment.parent / Comment.replies
    """

    __tablename__ = "comments"

    content: Mapped[str] = mapped_column(
        String(length=1000), nullable=False
    )
    status: Mapped[CommentStatus] = mapped_column(
        SqlEnum(CommentStatus, name="comment_status_enum"),
        default=CommentStatus.PB, nullable=False
    )

    # N:1 with User (backref: commenter)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.ID",
            name="fk_users_comments",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    # N:1 with Post (nullable) (backref: post)
    post_parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "posts.ID",
            name="fk_posts_comments",
            ondelete="CASCADE"
        ),
        nullable=True,  # NOTE: explained in docstring
        index=True
    )
    # N:1 with Comment (Self-Referencing) (nullable)
    comment_parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "comments.ID",
            name="fk_comments_reply_comments",
            ondelete="CASCADE"
        ),
        nullable=True,  # NOTE: explained in docstring
        index=True
    )
    # Self-referencing relationship
    parent: Mapped[Self] = relationship(
        "Comment",
        remote_side="Comment.ID",
        foreign_keys=[comment_parent_id],
        backref="replies"
    )
    # NOTE:
    # Comment.parent -> Self (if parent is a Comment)
    # Comment.replies -> list[Self]
