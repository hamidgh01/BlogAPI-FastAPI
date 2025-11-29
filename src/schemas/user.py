""" Schemas (Pydantic models) for 'User' Model """

from typing import Annotated, Optional, Literal
from re import fullmatch

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

from .GENERAL import Token

# --------------------------------------------------------------------
# Bases & Mixins:


class _SetPasswordOperationSchema(BaseModel):
    password: Annotated[str, Field(
        ..., min_length=8, max_length=64,
        description="Password (no whitespace characters, 8-64 characters)"
    )]
    confirm_password: Annotated[str, Field(
        ..., min_length=8, max_length=64,
        description="Password confirmation (must match password)"
    )]

    @field_validator("password", mode="before")
    @classmethod
    def check_password_pattern(cls, value: str) -> str:  # NOTE: value=password
        if not fullmatch(r"\S{8,64}", value):
            raise ValueError(
                "[password] can not include whitespace characters (space,"
                " newline, etc...)  |  length: '8 <= password <= 64'"
            )
        return value

    @field_validator("confirm_password")
    @classmethod
    def check_passwords_match(cls, value: str, info) -> str:
        # NOTE: value=confirm_password
        if ("password" in info.data) and (value == info.data["password"]):
            return value
        raise ValueError("Passwords don't match!")


class _CheckUsernamePatternValidatorMixin:

    @field_validator("username", mode="before")
    @classmethod
    def check_patterns(cls, value: str) -> str:
        if value and not fullmatch(r"[a-z0-9_]{3,64}", value):
            raise ValueError(
                "[username] allowed characters: 'a-z', '0-9', '_' "
                "(NO capital letters or spaces) | length: 3-64"
            )
        return value


# --------------------------------------------------------------------


class CreateUserSchema(
    _SetPasswordOperationSchema,
    _CheckUsernamePatternValidatorMixin
):
    username: Annotated[str, Field(
        ..., min_length=3, max_length=64,
        description="Unique username (only: 'a-z' , '0-9' , '_')"
    )]
    email: Annotated[EmailStr, Field(
        ..., description="Unique and valid email address"
    )]


class UpdateUserSchema(BaseModel, _CheckUsernamePatternValidatorMixin):
    username: Annotated[Optional[str], Field(
        None, min_length=3, max_length=64,
        description="Update username: Unique / only: 'a-z' , '0-9' , '_'"
    )]
    email: Annotated[Optional[EmailStr], Field(
        None, description="Update email: Unique and valid email address"
    )]


class UpdatePasswordSchema(_SetPasswordOperationSchema):
    old_password: Annotated[str, Field(
        ..., min_length=8, max_length=64,
        description="Password (no whitespace, 8-64 characters)"
    )]


class SetPasswordSchema(_SetPasswordOperationSchema):
    pass


class UserOutSchema(BaseModel):
    ID: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserLoginRequestSchema(BaseModel):
    identifier: Annotated[str, Field(
        ..., description="can be 'username' or 'email' of the User"
    )]
    password: Annotated[str, Field(..., description="password of the user")]


class LoginSuccessfulData(BaseModel):
    user: UserOutSchema
    token: Token

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------


class FollowSchema(BaseModel):
    # user_id: int (will be extracted form auth-token)
    # -> ID of user who wants to follow another one
    intended_user_id: Annotated[int, Field(
        ..., ge=1, description="ID of the intended user to 'follow'"
    )]


class UnfollowOrRemoveFollowerSchema(BaseModel):
    # user_id: int (it'll be extracted form auth-token)
    # -> ID of user who wants to unfollow another one or remove a follower
    operation_type: Annotated[
        Literal["unfollow", "remove"],
        Field(..., description="type of operation: 'unfollow' or 'remove'")
    ]
    intended_user_id: Annotated[int, Field(
        ..., ge=1,
        description="ID of the intended user to 'unfollow' or 'remove'"
    )]


class FollowerOrFollowingListSchema(BaseModel):
    users_list: Annotated[Optional[list[UserOutSchema]], Field(
        None, description="list of followers or followings"
    )]
