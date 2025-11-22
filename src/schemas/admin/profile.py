""" admin-specific 'Profile' schemas """

from typing import Annotated, Optional
from datetime import datetime, date

from pydantic import BaseModel, Field, ConfigDict

from src.models import Gender
from .user import UserListSchema, UserDetailsForAdminSchema
from ..profile import LinkOut


class ProfileListForAdminPanelSchema(BaseModel):
    """ NOTE: this schema includes field from both User and Profile models """
    user_id: Annotated[int, Field(..., description="PK of profile (User ID)")]
    display_name: Optional[str] = None
    created_at: datetime
    gender: Gender
    user: Annotated[UserListSchema, Field(
        ...,
        description="Contains username, id, is_active & is_superuser of User"
    )]

    model_config = ConfigDict(from_attributes=True)


class ProfileDetailsForAdminPanelSchema(ProfileListForAdminPanelSchema):
    """ NOTE: this schema includes field from both User and Profile models """
    about: Optional[str] = None
    updated_at: datetime  # Profile.updated_at
    birth_date: Optional[date] = None
    links: Annotated[Optional[list[LinkOut]], Field(
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
