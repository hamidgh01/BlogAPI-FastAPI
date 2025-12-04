""" admin-specific 'ReportOnUser' & 'ReportOnPost' schemas """

from typing import Annotated, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models import UserReportTitleChoices, PostReportTitleChoices


# ----------------------------------------------------------
# ReportOnUser Schemas


class ReportOnUserListOut(BaseModel):
    ID: int
    title: Annotated[UserReportTitleChoices, Field(
        ..., description="Title (report reason enum for users)")]
    reported_user_id: Annotated[int, Field(
        ..., description="ID of the reported-user"
    )]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportOnUserDetailsOut(ReportOnUserListOut):
    reporter_id: Annotated[Optional[int], Field(
        None, description="ID of reporter-user (nullable)"
    )]
    description: Optional[str] = None


# ----------------------------------------------------------
# ReportOnPost Schemas


class ReportOnPostListOut(BaseModel):
    ID: int
    title: Annotated[PostReportTitleChoices, Field(
        ..., description="Title (report reason enum for posts)")]
    reported_post_id: Annotated[int, Field(
        ..., description="ID of the reported-post"
    )]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportOnPostDetailsOut(ReportOnUserListOut):
    reporter_id: Annotated[Optional[int], Field(
        None, description="ID of reporter-user (nullable)"
    )]
    description: Optional[str] = None
