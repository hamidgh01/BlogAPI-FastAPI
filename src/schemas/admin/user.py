""" admin-specific 'User' schemas """

from typing import Annotated, Optional
from re import fullmatch
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class UpdateUserForAdminSchema(BaseModel):
    username: Annotated[Optional[str], Field(
        None, min_length=3, max_length=64,
        description="Update username: Unique / only: 'a-z' , '0-9' , '_'"
    )]
    email: Annotated[Optional[EmailStr], Field(
        None, description="Update email: Unique and valid email address"
    )]
    is_active: Annotated[bool | None, Field(
        ..., description="(Dangerous) suspend/activate a User"
    )]
    is_superuser: Annotated[bool | None, Field(
        ..., description="(too much Dangerous!!!) make a User as superuser"
    )]

    @field_validator("username", mode="before")
    @classmethod
    def check_patterns(cls, value: str) -> str:
        if value and not fullmatch(r"[a-z0-9_]{3,64}", value):
            raise ValueError(
                "[username] allowed characters: 'a-z', '0-9', '_' "
                "(NO capital letters or spaces) | length: 3-64"
            )
        return value


class UserListSchema(BaseModel):
    ID: int
    username: str
    is_active: Annotated[bool, Field(
        ..., description="user's activation: active(true)/suspend(false)"
    )]
    is_superuser: Annotated[bool, Field(
        ..., description="superuser-permission for a user (true/false)"
    )]

    model_config = ConfigDict(from_attributes=True)


class UserDetailsForAdminSchema(UserListSchema):
    email: EmailStr
    created_at: datetime
    updated_at: datetime
