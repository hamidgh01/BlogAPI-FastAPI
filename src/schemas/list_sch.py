""" Schemas (Pydantic models) for 'List' Model """

from typing import Annotated, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CreateListSchema(BaseModel):
    # user_id (owner) assigned from auth-token
    title: Annotated[str, Field(
        ..., min_length=2, max_length=120, description="List title"
    )]
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="List description"
    )]
    is_private: Annotated[bool, Field(
        default=True, description="Specifies the list is private or public"
    )]
    post_id: Annotated[Optional[int], Field(
        None, description="Initial post ID to add to the list"
    )]
    # post_ids: Annotated[Optional[List[int]], Field(...)]  # (maybe)


class UpdateListSchema(BaseModel):
    title: Annotated[Optional[str], Field(
        None, min_length=2, max_length=120, description="List title"
    )]
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="List description"
    )]
    is_private: Annotated[Optional[bool], Field(
        None, description="Specifies the list is private or public"
    )]


class ListListSchema(BaseModel):
    id: Annotated[int, Field(..., description="Unique ID")]
    title: Annotated[str, Field(..., description="Title")]
    is_private: Annotated[bool, Field(..., description="Privacy status")]
    created_at: Annotated[datetime, Field(
        ..., description="creation date and time (timestamp)"
    )]
    user_id: Annotated[int, Field(..., description="Owner user ID")]
    # Todo: add post_count field later

    model_config = ConfigDict(from_attributes=True)


class ListDetailsSchema(ListListSchema):
    description: Annotated[Optional[str], Field(
        None, max_length=1000, description="List description"
    )]

    model_config = ConfigDict(from_attributes=True)


# DeleteList...


class SaveOrUnsavePost(BaseModel):
    post_id: Annotated[int, Field(..., description="ID of intended post")]
    # post_ids: Annotated[list[int], Field(
    #     ..., description="ID of all intended posts"
    # )]  # maybe
    list_id: Annotated[int, Field(..., description="ID of intended list")]


class SaveOrUnsaveList(BaseModel):
    list_id: Annotated[int, Field(..., description="ID of intended list")]
    # user_id: Annotated[int, Field(
    #     ..., description="ID the user who wants to unsave the list"
    # )]  # it'll be extracted form auth-token
