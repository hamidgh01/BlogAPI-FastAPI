""" Schemas (Pydantic models) for 'Profile' & 'Link' Models """

from typing import Annotated, Optional
from datetime import date

from pydantic import BaseModel, Field, HttpUrl, ConfigDict

from src.models import Gender
from .user import UserOutSchema

# ----------------------------------------------------------
# Link Schemas (part of Profile)


class CreateLinkSchema(BaseModel):
    title: Annotated[str, Field(..., max_length=64, description="Link title")]
    url: Annotated[HttpUrl, Field(
        ..., description="Valid URL (scheme: 'http://' or 'https://')"
    )]
    profile_id: Annotated[int, Field(
        ..., description="related profile pk (profile.user_id)"
    )]


class UpdateLinkSchema(BaseModel):
    title: Annotated[Optional[str], Field(
        None, max_length=64, description="Link title"
    )]
    url: Annotated[Optional[HttpUrl], Field(
        None, description="Valid URL (scheme: 'http://' or 'https://')"
    )]
    profile_id: Annotated[int, Field(
        ..., description="related profile pk (profile.user_id)"
    )]  # NOTE: 'Link.profile_id' is needed for validating ownership
    # Link.profile_id -> Profile.user_id -> User.id -> link_owner_id
    # if link_owner_id == id from auth-token


class LinkOut(CreateLinkSchema):
    ID: Annotated[int, Field(..., description="Unique link ID")]
    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Profile Schemas


class UpdateProfileSchema(BaseModel):
    display_name: Annotated[Optional[str], Field(
        None, max_length=64, description="Display name (optional)"
    )]
    about: Annotated[Optional[str], Field(
        None, max_length=2000, description="Bio/about text (optional)"
    )]
    birth_date: Annotated[Optional[date], Field(
        None, description="Birth date (optional)"
    )]
    gender: Annotated[Optional[Gender], Field(
        None,
        description="Gender enum (male / female / other / not-specified)"
    )]


class ProfileListSchema(BaseModel):
    """ NOTE: this schema includes field from both User and Profile models """
    user_id: Annotated[int, Field(..., description="PK of profile (User ID)")]
    display_name: Optional[str] = None
    user: Annotated[UserOutSchema, Field(
        ..., description="Contains 'username' and 'id' of User model"
    )]
    # profile_photo

    model_config = ConfigDict(from_attributes=True)


class ProfileOutAfterUpdate(BaseModel):
    """ NOTE: this schema includes field from both User and Profile models """
    user_id: Annotated[int, Field(..., description="PK of profile (User ID)")]
    display_name: Optional[str] = None
    about: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Gender
    # profile_photo

    model_config = ConfigDict(from_attributes=True)


class ProfileDetailsSchema(ProfileOutAfterUpdate):
    """ NOTE: this schema includes field from both User and Profile models """
    user: Annotated[UserOutSchema, Field(
        ..., description="Contains 'username' and 'id' of User model"
    )]
    links: Annotated[Optional[list[LinkOut]], Field(
        None, description="list of profile's links (if there is any)"
    )]
    follower_count: int
    following_count: int
    post_count: int

    followed_by_viewer: Annotated[bool, Field(
        ...,
        description="indicates whether the current profile is followed "
                    "by the viewer (current user) or not (true/false)"
    )]

    # ToDo: complete this later:
    #   some recent 'posts'
    #   or maybe:
    #   pined + populars + recents (like YouTube) -> cached in redis


# ToDo: add this later
# class Me...  # current user's own profile
