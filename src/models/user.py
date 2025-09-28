from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    """
    Table/Model: User (users)
    Fields:
        id (PK), username, password, email,
        is_active, is_superuser, date_joined, updated_at

    Points/Notes:
        _ 'password' isn't stored in plain text. its hashed-value
          will be stored in database.
        _ 'email' is verified via Pydantic Schemas

    Relations:
        _ 1:N (One to Many) with 'Post' -> User.posts / Post.author
    """

    __tablename__ = "users"

    # id (defined in Base)
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
    date_joined: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )

    # 1:N with Post
    posts = relationship("Post", backref="author")
