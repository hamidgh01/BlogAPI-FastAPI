""" Schemas (Pydantic models) for 'Ticket' Model """

from typing import Annotated, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models.ticket import TicketStatus


class CreateTicketSchema(BaseModel):
    subject: Annotated[Optional[str], Field(
        None, max_length=120, description="Ticket subject (optional)"
    )]
    message: Annotated[str, Field(
        ..., min_length=1, max_length=4000, description="Ticket message"
    )]


class UpdateTicketStatusForAdminSchema(BaseModel):
    status: Annotated[TicketStatus, Field(
        ..., description="Ticket status enum: unread / read / closed"
    )]


class TicketListSchema(BaseModel):
    id: Annotated[int, Field(..., description="Unique Ticket ID")]
    subject: Annotated[Optional[str], Field(
        None, max_length=120, description="Ticket subject"
    )]
    status: Annotated[TicketStatus, Field(
        ..., description="Ticket status enum: unread / read / closed"
    )]
    created_at: Annotated[datetime, Field(
        ..., description="creation date and time (timestamp)"
    )]
    user_id: Annotated[Optional[int], Field(
        None, description="ID of sender user (nullable if deleted)"
    )]

    model_config = ConfigDict(from_attributes=True)


class TicketDetailsSchema(TicketListSchema):
    message: Annotated[str, Field(
        ..., min_length=1, max_length=4000, description="Ticket message"
    )]
