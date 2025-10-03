from enum import Enum as PythonEnum
from datetime import date

from sqlalchemy import (
    String, BigInteger, Date, ForeignKey, Index, Enum as SqlEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from ._mixins import UpdateAtFieldMixin


class Link(Base):
    """
    Table/Model: Link (links)
    Fields:
        id (PK), title, url, profile_id (FK) (actually profile_user_id)
    Notes:
        _ 'url' is verified via Pydantic Schemas
    Relations:
    _ N:1 (Many to One) with 'Profile' -> Link.related_profile / Profile.links
    """

    __tablename__ = "links"

    # id (defined in Base)
    title: Mapped[str] = mapped_column(String(length=64), nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)

    # N:1 with Profile (backref: related_profile)
    profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "profiles.user_id",
            name="fk_profile_links",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # ToDo: put limitation for number of links (e.g. 10 links) per profile


class Gender(PythonEnum):
    MA = "Male"
    FM = "Female"
    OT = "Other"
    NS = "Not-Specified"


class Profile(Base, UpdateAtFieldMixin):
    """
    Table/Model: Profile (profiles)
    Fields:
        user_id (PK & FK), display_name, about (bio),
        birth_date, gender, updated_at, profile_photo

    Points/Notes:
        _ there is no 'id' field in this model. instead the 'user_id' field
          (FK from User model) is PK for this model (automatically indexed,
          unique and one2one -> result: less indexed columns - lighter db)

    Relations:
    _ 1:1 (One to One) with 'User' -> Profile.user / User.profile
    _ 1:N (One to Many) with 'Link' -> Profile.links / Link.related_profile
    """

    __tablename__ = "profiles"

    id = None  # to make 'user_id' as PK

    # 1:1 with User (backref: user)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            name="user_profile_one2one",
            ondelete="CASCADE"
        ),
        nullable=False,
        # unique=True,  # makes it One to One
        # index=True,
        primary_key=True  # automatically "indexed", "unique" and one2one
    )

    display_name: Mapped[str] = mapped_column(
        String(length=64), nullable=True
    )  # this column is indexed (partial/filtered index) in '__table_args__'
    about: Mapped[str] = mapped_column(String(length=2000), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender] = mapped_column(
        SqlEnum(Gender, name="profile_gender_enum"), default=Gender.NS
    )
    # ToDo: add a 'created_at' field with default_factory=(a factory with
    #  this result: the value of 'created_at' field of its related user)
    # profile_photo: Mapped[...]  # ToDo: implement this later

    # 1:N with Link
    links: Mapped[Link] = relationship(
        "Link", backref="related_profile"
    )

    __table_args__ = (
        Index(
            'idx_display_name_not_null',
            'display_name',
            postgresql_where='display_name IS NOT NULL'
        ),  # partial/filtered index: only indexes non-NULL values.
    )
