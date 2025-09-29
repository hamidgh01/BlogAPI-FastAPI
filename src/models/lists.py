from datetime import datetime

from sqlalchemy import (
    String, DateTime, Boolean, ForeignKey, func,
    Table, Column, PrimaryKeyConstraint, BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class List(Base):
    """
    Table/Model: List (tags)
    Fields:
        id (PK), title, description, is_private,
        created_at, updated_at, user_id (FK) [owner]

    Relations:
    _ N:1 (Many to One) with 'User' (owner) -> List.owner / User.owned_lists
    """

    __tablename__ = "lists"

    # id (defined in Base)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(
        String(length=1000), nullable=True
    )
    is_private: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

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
