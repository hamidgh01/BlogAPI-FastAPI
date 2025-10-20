""" Schemas (Pydantic models) for 'Post' & 'Tag' Models """

from typing import Annotated, Optional
from re import compile
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.models import PostStatus
from .user import UserOutSchema


TAG_NAME_PATTERN = compile(r"^[ا-یa-z0-9_]{1,120}$")


def validate_tag_name(value: str) -> str:
    if not TAG_NAME_PATTERN.fullmatch(value.lower()):
        raise ValueError(
            "tag-name must match this pattern: ^[ا-یa-z0-9_]{1,120}$"
        )
    return value


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
                    "draft/published/rejected/deleted-by-author"
    )]
    # NOTE:
    # if status=DR -> published_at=null
    # if status=PB -> published_at: is set in backend
    # (a user can't draft a published post again! but it can make that private)
    # NOTE:
    # 'slug' and 'reading_time' is generated in backend

    tags: Annotated[Optional[list[str]], Field(
        default_factory=list,
        description="List of tag_names\n"
                    "each tag-name must be:\n"
                    "1 <= length <= 120\n"
                    "characters:\n"
                    "   Persian Alphabets (ا-ی)\n"
                    "   English-lowercase (a-z)\n"
                    "   numbers (0-9)\n"
                    "   _\n"
                    "(no white space characters)"
    )]

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags: list[str]) -> list[str]:
        return [validate_tag_name(tag) for tag in tags]


class UpdatePostSchema(BaseModel):
    title: Annotated[Optional[str], Field(
        None, min_length=2, max_length=250, description="Post title"
    )]
    content: Annotated[Optional[str], Field(
        None, description="Post content (text)"
    )]
    is_private: Annotated[Optional[bool], Field(
        default=False, description="being Private/Public (default: public)"
    )]
    tags: Annotated[Optional[list[str]], Field(
        default_factory=list,
        description="List of tag_names\n"
                    "each tag-name must be:\n"
                    "1 <= length <= 120\n"
                    "characters:\n"
                    "   Persian Alphabets (ا-ی)\n"
                    "   English-lowercase (a-z)\n"
                    "   numbers (0-9)\n"
                    "   _\n"
                    "(no white space characters)"
    )]

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags: list[str]) -> list[str]:
        return [validate_tag_name(tag) for tag in tags]


class ChangePostPrivacySchema(BaseModel):
    is_private: Annotated[bool, Field(..., description="being Private/Public")]


class UpdatePostStatusSchema(BaseModel):
    status: Annotated[PostStatus, Field(
        ...,
        description="Post status enum: "
                    "draft/published/rejected/deleted-by-author"
    )]
    # NOTE:
    # this schema is used for: when:
    # _ user publishes a draft-post -> status=PostStatus.PB ("Published")
    # _ user deletes a draft/published post -> status=PostStatus.DL ("Deleted")
    # _ admin rejects a post -> status=PostStatus.RJ ("Rejected")
    # (a user can't draft a published post again! but it can make that private)


class ReadTagSchema(BaseModel):  # for both 'tag_list' and 'tag_details'
    ID: Annotated[int, Field(..., description="unique tag ID")]
    name: Annotated[str, Field(..., description="unique tag name")]

    model_config = ConfigDict(from_attributes=True)


class PostListSchema(BaseModel):
    ID: int
    title: str
    slug: Optional[str] = None
    reading_time: Annotated[Optional[int], Field(
        None, description="Estimated reading time (seconds)"
    )]
    created_at: datetime
    published_at: Optional[datetime] = None

    user: Annotated[UserOutSchema, Field(
        ..., description="Contains 'username' and 'id' of related user"
    )]

    saved_by_viewer: Annotated[bool, Field(
        ...,
        description="indicates that the viewer (current user) "
                    "saved this post or not (true/false)"
    )]

    model_config = ConfigDict(from_attributes=True)


class PostDetailsSchema(PostListSchema):
    content: Optional[str] = None
    updated_at: datetime

    like_count: int
    comment_count: int
    tags: Optional[list[ReadTagSchema]] = None

    liked_by_viewer: Annotated[bool, Field(
        ...,
        description="indicates that the viewer (current user) "
                    "liked this post or not (true/false)"
    )]


class LikeUnlikePostSchema(BaseModel):
    post_id: Annotated[int, Field(..., description="post ID to like/unlike")]
    # user_id: int
    #   -> ID of the user who wants to like or unlike a post
    #   -> it'll be extracted form auth-token
