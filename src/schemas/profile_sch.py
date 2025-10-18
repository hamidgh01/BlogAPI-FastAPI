""" Schemas (Pydantic models) for 'Profile' & 'Link' Models """

from typing import Annotated, Optional
from datetime import date

from pydantic import BaseModel, Field, HttpUrl, ConfigDict

from src.models import Gender

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
