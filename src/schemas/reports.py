""" Schemas (Pydantic models) for 'ReportOnUser' & 'ReportOnPost' Models """

from typing import Annotated, Optional

from pydantic import BaseModel, Field

from src.models import UserReportTitleChoices, PostReportTitleChoices


class ReportOnUserIn(BaseModel):
    title: Annotated[UserReportTitleChoices, Field(
        ..., description="Report reason enum for users"
    )]
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="Report description"
    )]
    reported_user_id: Annotated[int, Field(
        ..., description="ID of the reported-user"
    )]
    # reporter_id from auth-token


class ReportOnPostIn(BaseModel):
    title: Annotated[PostReportTitleChoices, Field(
        ..., description="Report reason enum for posts"
    )]
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="Report description"
    )]
    reported_post_id: Annotated[int, Field(
        ..., description="ID of the reported-post"
    )]
    # reporter_id from auth-token
