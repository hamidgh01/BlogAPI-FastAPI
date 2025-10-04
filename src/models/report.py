from enum import Enum as PythonEnum

from sqlalchemy import BigInteger, String, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from ._mixins import CreatedAtFieldMixin


class _BaseReport:
    """ Base Class for Report Models (ReportOnUser and ReportOnPost) """
    title = NotImplemented  # must be implemented in SubClasses
    description: Mapped[str] = mapped_column(
        String(length=1000), nullable=True
    )
    # N:1 with User (as reporter)
    # (`backref` in both ReportOnUser and ReportOnPost: "reporter")
    reporter_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.ID",
            name="fk_users_reports_for_reporter",
            ondelete="SET NULL"
        ),
        nullable=True  # due to ondelete="SET NULL"
    )


class UserReportTitleChoices(PythonEnum):
    R1 = "User-Report Reason 1"
    R2 = "User-Report Reason 2"
    R3 = "User-Report Reason 3"
    R4 = "User-Report Reason 4"
    R5 = "User-Report Reason 5"
    R6 = "User-Report Reason 6"
    OT = "Other"


class ReportOnUser(Base, _BaseReport, CreatedAtFieldMixin):
    """
    Table/Model: ReportOnUser (reports_on_users)

    Fields:
        ID (PK), title, description, reporter_id (FK),
        created_at, reported_user_id (FK)

    Points/Notes:
    _ 'ReportOnUser' Model has 2 different relationships with User Model:
        first: FK with User as reporter (NOT NULL -unless a user is deleted-)
        second: FK with User as reported_user (NOT NULL)

    Relations:
    _ N:1 (Many to One) with 'User' (as reporter)
      -> ReportOnUser.reporter / User.reports_on_users
    _ N:1 (Many to One) with 'User' (as reported_user)
      -> ReportOnUser.reported_user / User.received_reports
    """

    __tablename__ = "reports_on_users"

    title: Mapped[UserReportTitleChoices] = mapped_column(
        SqlEnum(
            UserReportTitleChoices,
            name="user_report_title_choices_enum"
        ),
        nullable=False
    )

    # N:1 with User (as reported_user) (nullable) (backref: reported_user)
    reported_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.ID",
            name="fk_users_reports_for_reported_users",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


class PostReportTitleChoices(PythonEnum):
    R1 = "Post-Report Reason 1"
    R2 = "Post-Report Reason 2"
    R3 = "Post-Report Reason 3"
    R4 = "Post-Report Reason 4"
    R5 = "Post-Report Reason 5"
    R6 = "Post-Report Reason 6"
    OT = "Other"


class ReportOnPost(Base, _BaseReport, CreatedAtFieldMixin):
    """
    Table/Model: ReportOnPost (reports_on_posts)

    Fields:
        ID (PK), title, description, reporter_id (FK),
        created_at, reported_post_id (FK)

    Relations:
    _ N:1 (Many to One) with 'User' (as reporter)
      -> ReportOnPost.reporter / User.reports_on_posts
    _ N:1 (Many to One) with 'Post'
      -> ReportOnPost.reported_post / ReportOnPost.received_reports
    """

    __tablename__ = "reports_on_posts"

    title: Mapped[PostReportTitleChoices] = mapped_column(
        SqlEnum(
            PostReportTitleChoices,
            name="post_report_title_choices_enum"
        ),
        nullable=False
    )

    # N:1 with Post (backref: reported_post)
    reported_post_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "posts.ID",
            name="fk_posts_reports",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )
