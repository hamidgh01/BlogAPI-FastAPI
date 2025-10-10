""" Schemas (Pydantic models) for 'ReportOnUser' & 'ReportOnPost' Models """

from typing import Annotated, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models import UserReportTitleChoices, PostReportTitleChoices

# ----------------------------------------------------------
# ReportOnUser Schemas


class CreateReportOnUserSchema(BaseModel):
    title: Annotated[UserReportTitleChoices, Field(
        ..., description="Report reason enum for users"
    )]
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="Report description"
    )]
    reported_user_id: Annotated[int, Field(
        ..., description="ID of the reported user"
    )]
    # reporter_id from auth-token


class ReportOnUserListSchema(BaseModel):
    id: Annotated[int, Field(..., description="Report-obj ID")]
    title: Annotated[UserReportTitleChoices, Field(
        ..., description="Title (report reason enum for users)")]
    reported_user_id: Annotated[int, Field(
        ..., description="ID of the reported user"
    )]
    created_at: Annotated[datetime, Field(
        ..., description="Created date and time (timestamp)"
    )]

    model_config = ConfigDict(from_attributes=True)


class ReportOnUserDetailsSchema(ReportOnUserListSchema):
    reporter_id: Annotated[Optional[int], Field(
        None, description="Reporter user ID (nullable)"
    )]
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="Report description"
    )]


# DeleteReport...

# ----------------------------------------------------------
# ReportOnPost Schemas


class CreateReportOnPostSchema(BaseModel):
    title: Annotated[PostReportTitleChoices, Field(
        ..., description="Report reason enum for posts"
    )]
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="Report description"
    )]
    reported_post_id: Annotated[int, Field(
        ..., description="ID of the reported post"
    )]
    # reporter_id from auth-token


class ReportOnPostListSchema(BaseModel):
    id: Annotated[int, Field(..., description="Report-obj ID")]
    title: Annotated[PostReportTitleChoices, Field(
        ..., description="Title (report reason enum for posts)")]
    reported_post_id: Annotated[int, Field(
        ..., description="ID of the reported post"
    )]
    created_at: Annotated[datetime, Field(
        ..., description="Created date and time (timestamp)"
    )]

    model_config = ConfigDict(from_attributes=True)


class ReportOnPostDetailsSchema(ReportOnUserListSchema):
    reporter_id: Annotated[Optional[int], Field(
        None, description="Reporter user ID (nullable)"
    )]
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="Report description"
    )]


# DeleteReport...
