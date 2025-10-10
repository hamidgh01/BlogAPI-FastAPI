""" Schemas (Pydantic models) for 'Profile' & 'Link' Models """

from typing import Annotated, Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict

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
# Profile Schemas...
