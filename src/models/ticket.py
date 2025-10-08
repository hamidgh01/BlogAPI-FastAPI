from enum import Enum as PythonEnum

from sqlalchemy import BigInteger, String, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from ._mixins import CreatedAtFieldMixin


class TicketStatus(PythonEnum):
    N = "unread"  # "hasn't been read"
    R = "read"  # "has been read"
    C = "closed"


class Ticket(Base, CreatedAtFieldMixin):
    """
    Table/Model: Ticket (tickets)
    Fields:
        ID (PK), user_id (FK) [sender], subject, message, created_at, status
    Relations:
        _ N:1 (Many to One) with 'User' -> Ticket.sender / User.tickets
    """

    __tablename__ = "tickets"

    subject: Mapped[str] = mapped_column(String(length=120), nullable=True)
    message: Mapped[str] = mapped_column(String(length=4000), nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        SqlEnum(TicketStatus, name="ticket_status_enum"),
        default=TicketStatus.N, nullable=False
    )

    # N:1 with User (backref: sender)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.ID",
            name="fk_users_tickets",
            ondelete="SET NULL"
        ),
        nullable=True,
    )
