""" admin-specific 'Ticket' schemas """

from typing import Annotated, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models import TicketStatus


class TicketListOut(BaseModel):
    ID: int
    subject: Optional[str] = None
    status: Annotated[TicketStatus, Field(
        ..., description="Ticket status enum: unread / read / closed"
    )]
    created_at: datetime
    user_id: Annotated[Optional[int], Field(
        None, description="ID of sender user (nullable if user is deleted)"
    )]

    model_config = ConfigDict(from_attributes=True)


class TicketDetailsOut(TicketListOut):
    message: str


class TicketUpdateStatus(BaseModel):
    status: Annotated[TicketStatus, Field(
        ..., description="Ticket status enum: unread / read / closed"
    )]
