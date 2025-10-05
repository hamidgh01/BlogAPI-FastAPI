from sqlalchemy import Table, Column, ForeignKey, BigInteger, DateTime, func

from .base import Base


# 'follows' association table -> M2M between 'users' and 'users'.
# NOTE: PK here is the combination of "follower_id" and "following_id".
follows = Table(
    "follows",
    Base.metadata,
    Column(
        "follower_id",
        BigInteger,
        ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        "following_id",
        BigInteger,
        ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        name="followed_at",
        type_=DateTime,
        server_default=func.now()
    )
)
# NOTE: 'primary_key=True' in both columns --> makes a composite_key of them
