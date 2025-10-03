from sqlalchemy import String, Boolean, ForeignKey, Table, Column, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from ._mixins import CreatedAtFieldMixin, UpdateAtFieldMixin


# 'saved_posts' association table -> M2M between 'posts' and 'lists'.
# NOTE: PK here is the combination of "list_id" and "post_id".
saved_posts = Table(
    "saved_posts",
    Base.metadata,
    Column(
        "list_id",
        ForeignKey("lists.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        "post_id",
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
)
# NOTE: 'primary_key=True' in both columns --> makes a composite_key of them


# 'user_saved_lists' association table -> M2M between 'users' and 'lists'.
# NOTE: PK here is the combination of "list_id" and "user_id".
user_saved_lists = Table(
    "user_saved_lists",
    Base.metadata,
    Column(
        "list_id",
        ForeignKey("lists.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
)


class List(Base, CreatedAtFieldMixin, UpdateAtFieldMixin):
    """
    Table/Model: List (lists)
    Fields:
        id (PK), title, description, is_private,
        created_at, updated_at, user_id (FK) [owner]

    Relations:
    _ N:1 (Many to One) with 'User' (owner) -> List.owner / User.owned_lists
    _ N:N (Many to Many) with 'Post' -> List.posts / Post.lists
      (via 'saved_posts' association table)
    _ N:N (Many to Many) with 'User'
      -> User.saved_lists / List.users_who_saved_this_list (almost useless)
      (via 'user_saved_lists' association table)
    """

    __tablename__ = "lists"

    # id (defined in Base)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(
        String(length=1000), nullable=True
    )
    is_private: Mapped[bool] = mapped_column(Boolean, default=True)

    # N:1 with User (backref: owner)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            name="fk_users_owned_lists",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # N:N with Post
    posts = relationship(
        "Post",
        secondary=saved_posts,
        back_populates="lists"
    )
    # N:N with User
    users_who_saved_this_list = relationship(
        "User",
        secondary=user_saved_lists,
        back_populates="saved_lists"
    )
