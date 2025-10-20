""" Schemas (Pydantic models) for 'Ticket' Model """

from typing import Annotated, Optional

from pydantic import BaseModel, Field


class CreateTicketSchema(BaseModel):
    subject: Annotated[Optional[str], Field(
        None, max_length=120, description="Ticket subject (optional)"
    )]
    message: Annotated[str, Field(
        ..., min_length=1, max_length=4000, description="Ticket message"
    )]
