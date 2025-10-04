from sqlalchemy import BigInteger, Identity
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    """ BaseClass for declaring other tables """
    # same ID for all Tables
    # for Tables with different ID: you can override 'ID' attribute
    ID: Mapped[int] = mapped_column(
        BigInteger, Identity(start=1, increment=1), primary_key=True
    )
    # NOTE:
    # no need for:
    # _ nullable=False, unique=True, autoincrement=True -> Identity(...)
    # _ index=True -> Postgres automatically indexes Primary Key
