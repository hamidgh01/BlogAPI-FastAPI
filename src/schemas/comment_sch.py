""" Schemas (Pydantic models) for 'Comment' Model """

from typing import Annotated, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from src.models import CommentStatus


class ParentType(Enum):
    P = "post"
    C = "comment"


class CreateCommentSchema(BaseModel):
    content: Annotated[str, Field(
        ..., min_length=1, max_length=1000, description="comment content"
    )]
    parent_type: Annotated[ParentType, Field(
        ..., description="specifies parent-type (can be 'post' or 'comment')"
    )]
    parent_id: Annotated[int, Field(
        ..., description="ID of parent-obj ('post_id' or 'comment_id')"
    )]


class UpdateCommentContentSchema(BaseModel):
    content: Annotated[Optional[str], Field(
        None, min_length=1, max_length=1000, description="updated content"
    )]


class UpdateCommentStatusSchema(BaseModel):
    """ this Schema is used when:
    _ admin 'hides' a comment  -> "Hidden-by-Admin"
    _ admin 'unhide' a comment  -> "published"
    _ commenter 'deletes' his/her comment  -> "Deleted-By-Commenter" """

    status: Annotated[CommentStatus, Field(
        ..., description="Comment status enum: "
                         "published / Hidden-by-Admin / Deleted-By-Commenter"
    )]


class CommentListSchema(BaseModel):  # is used is in admin-panel
    id: Annotated[int, Field(..., description="Unique Comment ID")]
    user_id: Annotated[int, Field(..., description="Commenter user ID")]
    content: Annotated[str, Field(
        ..., description="Comment content (truncated)"
    )]
    status: Annotated[CommentStatus, Field(
        ..., description="Comment status enum: "
                         "published / Hidden-by-Admin / Deleted-By-Commenter"
    )]
    created_at: Annotated[datetime, Field(
        ..., description="Creation timestamp"
    )]
    parent_type: Annotated[ParentType, Field(
        ..., description="specifies parent-type (can be 'post' or 'comment')"
    )]
    parent_id: Annotated[int, Field(
        ..., description="ID of parent-obj ('post_id' or 'comment_id')"
    )]

    model_config = ConfigDict(from_attributes=True)


class CommentDetailsSchema(CommentListSchema):
    content: Annotated[str, Field(
        ..., min_length=1, max_length=1000, description="Comment content"
    )]
    updated_at: Annotated[datetime, Field(
        ..., description="Last update timestamp"
    )]
