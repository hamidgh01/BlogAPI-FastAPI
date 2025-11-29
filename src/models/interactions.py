from sqlalchemy import Table, Column, ForeignKey, BigInteger, DateTime, func

from .base import Base


# 'follows' association table -> M2M between 'users' and 'users'.
# NOTE: PK here is the combination of "followed_by" and "followed".
follows = Table(
    "follows",
    Base.metadata,
    Column(
        "followed_by",  # user who follows another one
        BigInteger,
        ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        "followed",  # user who is followed
        BigInteger,
        ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        name="follow_at",
        type_=DateTime,
        server_default=func.now()
    )
)
# NOTE: 'primary_key=True' in both columns --> makes a composite_key of them


# 'post_likes' association table -> M2M between 'users' and 'posts'.
# NOTE: PK here is the combination of "post_id" and "user_id".
post_likes = Table(
    "post_likes",
    Base.metadata,
    Column(
        "post_id",
        BigInteger,
        ForeignKey("posts.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        "user_id",
        BigInteger,
        ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        name="liked_at",
        type_=DateTime,
        server_default=func.now()
    )
)
