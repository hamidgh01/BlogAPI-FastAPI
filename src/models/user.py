from __future__ import annotations
from typing import Self, TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from ._mixins import CreatedAtFieldMixin, UpdateAtFieldMixin
from .lists import user_saved_lists
from .interactions import follows, post_likes

if TYPE_CHECKING:
    from . import (
        Profile,
        Post,
        Comment,
        List,
        Ticket,
        ReportOnUser,
        ReportOnPost
    )


class User(Base, CreatedAtFieldMixin, UpdateAtFieldMixin):
    """
    Table/Model: User (users)
    Fields:
        ID (PK), username, password, email,
        is_active, is_superuser, created_at, updated_at

    Points/Notes:
        _ 'password' isn't stored in plain text. its hashed-value
          will be stored in database.
        _ 'email' is verified via Pydantic Schemas

    Relations:
    _ 1:1 (One to One) with 'Profile' -> User.profile / Profile.user
    _ 1:N (One to Many) with 'Post' -> User.posts / Post.author
    _ 1:N (One to Many) with 'Comment' -> User.comment / Comment.commenter
    _ 1:N with 'List' (owned-lists) -> User.owned_lists / List.owner
    _ N:N (Many to Many) with 'List' (saved-lists)
      -> User.saved_lists / List.users_who_saved_this_list
      (via 'user_saved_lists' association table)
    _ 1:N (One to Many) with 'Ticket' -> User.tickets / Ticket.sender
    relations with 'ReportOnUser':
        _ 1:N (One to Many) with 'ReportOnUser' (as reporter)
          -> User.reports_on_users / ReportOnUser.reporter
        _ 1:N (One to Many) with 'ReportOnUser' (as reported_user)
          -> User.received_reports / ReportOnUser.reported_user
    relation with 'ReportOnPost':
        _ 1:N (One to Many) with 'ReportOnPost' (as reporter)
          -> User.reports_on_posts / ReportOnPost.reporter
    _ N:N (Many to Many) with 'User' (itself) (follow-system)
      -> User.followings / User.followers (via 'follows' association table)
    _ N:N (Many to Many) with 'Post' (like-system)
      -> User.liked_posts / Post.likers (via 'post_likes' association table)
    """

    __tablename__ = "users"

    # ID (defined in Base)
    username: Mapped[str] = mapped_column(
        String(length=64),
        nullable=False,
        unique=True,
        index=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # date_joined: Mapped[datetime] = CreatedAtFieldMixin.created_at  # alias
    # created_at = None

    # 1:N with Post
    posts: Mapped[list[Post]] = relationship(
        "Post", backref="author"
    )
    # 1:N with Comment
    comments: Mapped[list[Comment]] = relationship(
        "Comment", backref="commenter"
    )
    # 1:N with List (owned-lists)
    owned_lists: Mapped[list[List]] = relationship(
        "List", backref="owner"
    )
    # N:N with List ('user_saved_lists' association table)
    saved_lists: Mapped[list[List]] = relationship(
        "List",
        secondary=user_saved_lists,
        back_populates="users_who_saved_this_list"
    )
    # 1:1 with Profile
    profile: Mapped[Profile] = relationship(
        "Profile", backref="user", uselist=False
    )
    # 1:N with Ticket
    tickets: Mapped[list[Ticket]] = relationship(
        "Ticket", backref="sender"
    )
    # ------------------------------------------------------
    # 1:N with ReportOnUser (as reporter -reports this user created-)
    reports_on_users: Mapped[list[ReportOnUser]] = relationship(
        "ReportOnUser",
        foreign_keys='ReportOnUser.reporter_id',  # which FK to use
        backref="reporter",
    )
    # 1:N with ReportOnUser (as reported_user -reports made against this user-)
    received_reports: Mapped[list[ReportOnUser]] = relationship(
        "ReportOnUser",
        foreign_keys='ReportOnUser.reported_user_id',  # which FK to use
        backref="reported_user"
    )
    # ---------------------------------------
    # 1:N with ReportOnPost (as reporter)
    reports_on_posts: Mapped[list[ReportOnPost]] = relationship(
        "ReportOnPost", backref="reporter"
    )
    # ------------------------------------------------------
    # N:N with User itself (Follower:Following) ('follows' association table)
    followings: Mapped[list[Self]] = relationship(
        "User",
        secondary=follows,
        primaryjoin=lambda: User.ID == follows.c.follower_id,
        secondaryjoin=lambda: User.ID == follows.c.following_id,
        backref="followers"
    )
    # N:N with Post (like-system) ('post_likes' association table)
    liked_posts: Mapped[list[Post]] = relationship(
        "Post",
        secondary=post_likes,
        back_populates="likers"
    )
