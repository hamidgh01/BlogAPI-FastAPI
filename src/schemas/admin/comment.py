""" admin-specific 'Comment' schemas """

from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models import CommentStatus


class CommentListOut(BaseModel):
    ID: int
    user_id: int
    content: Annotated[str, Field(
        ..., description="(truncated) comment content"
    )]
    status: Annotated[CommentStatus, Field(
        ..., description="Comment status enum: "
                         "published / Hidden-by-Admin / Deleted-By-Commenter"
    )]
    created_at: datetime
    # parent_type: Annotated[Literal["post", "comment"], Field(
    #     ..., description="specifies parent-type (can be 'post' or 'comment')"
    # )]
    # parent_id: Annotated[int, Field(
    #     ..., description="ID of parent-obj ('post_id' or 'comment_id')"
    # )]
    # # OR:
    # comment_parent_id: Optional[int] = None
    # post_parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
