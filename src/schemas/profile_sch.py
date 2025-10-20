""" Schemas (Pydantic models) for 'Profile' & 'Link' Models """

from typing import Annotated, Optional
from datetime import datetime, date

from pydantic import BaseModel, Field, HttpUrl, ConfigDict

from src.models import Gender
from .user_sch import (
    UserOutForClientSchema,
    UserListForAdminSchema,
    UserDetailsForAdminSchema
)

# ----------------------------------------------------------
# Link Schemas (part of Profile)


class _BaseLinkSchema(BaseModel):
    title: Annotated[str, Field(..., max_length=64, description="Link title")]
    url: Annotated[HttpUrl, Field(
        ..., description="Valid URL (scheme: 'http://' or 'https://')"
    )]
    profile_id: Annotated[int, Field(
        ..., description="related profile pk (profile.user_id)"
    )]


class CreateLinkSchema(_BaseLinkSchema):
    pass


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


# DeleteLinkSchema


class LinkListSchema(_BaseLinkSchema):
    id: Annotated[int, Field(..., description="Unique link ID")]
    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Profile Schemas


class _BaseProfileSchema(BaseModel):
    display_name: Annotated[Optional[str], Field(
        None, max_length=64, description="Display name (optional)"
    )]
    about: Annotated[Optional[str], Field(
        None, max_length=2000, description="Bio/about text (optional)"
    )]
    birth_date: Annotated[Optional[date], Field(
        None, description="Birth date (optional)"
    )]
    gender: Annotated[Gender, Field(
        default=Gender.NS,
        description="Gender enum (male / female / other / not-specified)"
    )]
    # profile_photo


class InitialProfileSchema(_BaseProfileSchema):
    """
    Since Profile is 1:1 with User, create-profile is tied to user creation.
    after creating user (and then profile object using 'user_id'):
    as the next step: user can fill out profile fields (separated request)
    """
    pass


class UpdateProfileSchema(_BaseProfileSchema):
    # All fields optional for partial updates
    pass


# ------------------------------------------------
# read for Client


class ProfileListForClientSchema(BaseModel):
    """ NOTE: this schema includes field from both User and Profile models """
    user_id: Annotated[int, Field(..., description="PK of profile (User ID)")]
    display_name: Optional[str] = None
    user: Annotated[UserOutForClientSchema, Field(
        ..., description="Contains 'username' and 'id' of User model"
    )]
    # profile_photo

    model_config = ConfigDict(from_attributes=True)


class ProfileDetailsForClientSchema(ProfileListForClientSchema):
    """ NOTE: this schema includes field from both User and Profile models """
    about: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Gender
    links: Annotated[Optional[list[LinkListSchema]], Field(
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

# ------------------------------------------------
# read for Admin


class ProfileListForAdminPanelSchema(BaseModel):
    """ NOTE: this schema includes field from both User and Profile models """
    user_id: Annotated[int, Field(..., description="PK of profile (User ID)")]
    display_name: Optional[str] = None
    created_at: Annotated[datetime, Field(
        ..., description="creation date and time (timestamp)"
    )]
    gender: Gender
    user: Annotated[UserListForAdminSchema, Field(
        ...,
        description="Contains username, id, is_active & is_superuser of User"
    )]

    model_config = ConfigDict(from_attributes=True)


class ProfileDetailsForAdminPanelSchema(ProfileListForAdminPanelSchema):
    """ NOTE: this schema includes field from both User and Profile models """
    about: Optional[str] = None
    updated_at: datetime  # Profile.updated_at
    birth_date: Optional[date] = None
    links: Annotated[Optional[list[LinkListSchema]], Field(
        None, description="list of profile's links (if there is any)"
    )]

    # NOTE: overriding 'user' from ProfileListForAdminPanelSchema
    user: Annotated[UserDetailsForAdminSchema, Field(
        ...,
        description="Contains username, id, is_active, is_superuser, email,"
                    "created_at & updated_at of User model"
    )]

    # follower_count: int
    # following_count: int
    # 'posts'
    # 'comments' ???

    # profile_photo
