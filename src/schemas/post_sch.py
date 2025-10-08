""" Schemas (Pydantic models) for 'Post' & 'Tag' Models """

from typing import Annotated, List, Optional
from re import fullmatch

from pydantic import (
    BaseModel, Field, field_validator, ConfigDict
)

from src.models import PostStatus

# --------------------------------------------------------------------

# Tag Schemas:


class CreateTagSchema(BaseModel):
    name: Annotated[str, Field(
        ..., min_length=1, max_length=120, description="unique tag name"
    )]

    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        if value and not fullmatch(r"[ا-یa-zA-Z0-9_]{1,120}", value):
            raise ValueError("[name] length <= 120  |  allowed characters: "
                             "Persian/English Alphabets , numbers , _ ")
        return value
    # NOTE:
    # because of 'mode="after"' in above field_validator, and 'max_length=120'
    # in 'name' field --> 'length <= 120' is validated by Pydantic itself


class ReadTagSchema(BaseModel):  # for both 'tag_list' and 'tag_details'
    id: Annotated[int, Field(..., description="unique tag ID")]
    name: Annotated[str, Field(..., description="unique tag name")]

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------

# Post Schemas:


class CreatePostSchema(BaseModel):
    title: Annotated[str, Field(
        ..., min_length=2, max_length=250, description="Post title"
    )]
    content: Annotated[Optional[str], Field(
        None, description="Post content (text)"
    )]
    is_private: Annotated[bool, Field(
        default=False, description="being Private/Public (default: public)"
    )]
    status: Annotated[PostStatus, Field(
        default=PostStatus.DR,
        description="Post status enum "
                    "(PostStatus.DR -> 'Draft' / PostStatus.PB -> 'Published')"
    )]
    # NOTE:
    # if status=DR -> published_at=null
    # if status=PB -> published_at: is set in backend
    # (a user can't draft a published post again! but it can make that private)
    # NOTE:
    # 'slug' and 'reading_time' is generated in backend

    tags: Annotated[Optional[List[str | int]], Field(
        None, description="List of tag_id (existing tags) or "
                          "tag_names (not exists -> will be created)"
    )]  # int -> tag_id -> existing tag / str -> tag_name -> creating new tag


class UpdatePostSchema(BaseModel):
    title: Annotated[Optional[str], Field(
        None, min_length=2, max_length=250, description="Post title"
    )]
    content: Annotated[Optional[str], Field(
        None, description="Post content (text)"
    )]
    tags: Annotated[Optional[List[str | int]], Field(
        None, description="List of tag_id (existing) or tag_names (to create)"
    )]
    is_private: Annotated[Optional[bool], Field(
        default=False, description="being Private/Public (default: public)"
    )]


class ChangePostPrivacySchema(BaseModel):
    is_private: Annotated[bool, Field(..., description="being Private/Public")]


class UpdatePostStatusSchema(BaseModel):
    status: Annotated[PostStatus, Field(..., description="...")]
    # NOTE:
    # this schema is used for: when:
    # _ user publishes a draft-post -> status=PostStatus.PB ("Published")
    # _ user deletes a draft/published post -> status=PostStatus.DL ("Deleted")
    # _ admin rejects a post -> status=PostStatus.RJ ("Rejected")
    # (a user can't draft a published post again! but it can make that private)
