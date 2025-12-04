""" Schemas (Pydantic models) for 'Comment' Model """

from typing import Annotated, Optional, Literal
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CommentCreate(BaseModel):
    content: Annotated[str, Field(
        ..., min_length=1, max_length=1000, description="comment content"
    )]
    parent_type: Annotated[
        Literal["post", "comment"],
        Field(..., description="specifies parent-type ('post' or 'comment')")
    ]
    parent_id: Annotated[int, Field(
        ..., description="ID of parent-obj ('post_id' or 'comment_id')"
    )]


class CommentUpdate(BaseModel):
    content: Annotated[Optional[str], Field(
        None, min_length=1, max_length=1000, description="updated content"
    )]


class CommentOut(BaseModel):
    ID: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    parent_type: Annotated[
        Literal["post", "comment"],
        Field(..., description="specifies parent-type ('post' or 'comment')")
    ]
    parent_id: Annotated[int, Field(
        ..., description="ID of parent-obj ('post_id' or 'comment_id')"
    )]

    model_config = ConfigDict(from_attributes=True)
