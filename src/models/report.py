from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class _BaseReport:
    """ Base Class for Report Models (ReportOnUser and ReportOnPost) """
    title = NotImplemented  # must be implemented in SubClasses
    description: Mapped[str] = mapped_column(
        String(length=1000), nullable=True
    )
    # N:1 with User (as reporter)
    reporter_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            name="fk_users_reports_for_reporter",
            ondelete="SET NULL"
        ),
        nullable=True
    )
