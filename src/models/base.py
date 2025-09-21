from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """ BaseClass for declaring other tables """
    # same ID for all Tables
    # for Tables with different ID: you can override 'id' attribute
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, index=True,
    )  # NOTE: 'nullable=False' & 'unique=True' are automatically applied.
