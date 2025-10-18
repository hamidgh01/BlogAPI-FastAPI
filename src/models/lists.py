from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger, String, Boolean, DateTime, func, ForeignKey, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from ._mixins import CreatedAtFieldMixin, UpdateAtFieldMixin

if TYPE_CHECKING:
    from . import User, Post


# 'saved_posts' association table -> M2M between 'posts' and 'lists'.
# NOTE: PK here is the combination of "list_id" and "post_id".
saved_posts = Table(
    "saved_posts",
    Base.metadata,
    Column(
        "list_id",
        ForeignKey("lists.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        "post_id",
        ForeignKey("posts.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        name="saved_date",
        type_=DateTime,
        server_default=func.now()
    )
)
# NOTE: 'primary_key=True' in both columns --> makes a composite_key of them


# 'user_saved_lists' association table -> M2M between 'users' and 'lists'.
# NOTE: PK here is the combination of "list_id" and "user_id".
user_saved_lists = Table(
    "user_saved_lists",
    Base.metadata,
    Column(
        "list_id",
        ForeignKey("lists.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        "user_id",
        ForeignKey("users.ID", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    ),
    Column(
        name="saved_date",
        type_=DateTime,
        server_default=func.now()
    )
)


class List(Base, CreatedAtFieldMixin, UpdateAtFieldMixin):
    """
    Table/Model: List (lists)
    Fields:
        ID (PK), title, description, is_private,
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

    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(
        String(length=1000), nullable=True
    )
    is_private: Mapped[bool] = mapped_column(Boolean, default=True)

    # ToDo: add a post_count column -> avoid querying database to count number
    #  of Posts in each List for 'saved-lists' or 'owned-lists' routes

    # ToDo: add 'pin' column with limitation=10 (for example)

    # ToDo: probably delete 'updated_at' field / or maybe don't delete
    # NOTE (important) : the 'last-update' value for a list
    # will be the last time a post added to that list:
    # -> MAX(saved_date) for saved_posts in a list

    # N:1 with User (backref: owner)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.ID",
            name="fk_users_owned_lists",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # N:N with Post ('saved_posts' association table)
    posts: Mapped[list[Post]] = relationship(
        "Post",
        secondary=saved_posts,
        back_populates="lists"
    )
    # N:N with User ('user_saved_lists' association table)
    users_who_saved_this_list: Mapped[list[User]] = relationship(
        "User",
        secondary=user_saved_lists,
        back_populates="saved_lists"
    )
