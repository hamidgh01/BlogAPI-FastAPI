from .user import (
    UserCreate,
    UserUpdate,
    UpdatePassword,
    SetPassword,
    UserOut,
    UserLoginRequest,
    LoginSuccessfulData,
    FollowCreate,
    UnfollowOrRemoveFollowerSchema,
    FollowerOrFollowingListOut,
)
from .post import (
    TagsIn,
    PostCreate,
    PostUpdate,
    ChangePostPrivacy,
    PostUpdateStatus,
    TagOut,
    PostOut,
    PostListOut,
    PostDetailsOut,
    LikeUnlikePost
)
from .comment import CommentCreate, CommentUpdate, CommentOut
from .list import (
    ListCreate,
    ListUpdate,
    ListListOut,
    ListDetailsOut,
    SaveOrUnsavePost,
    SaveOrUnsaveList
)
from .profile import (
    LinkCreate,
    LinkUpdate,
    LinkOut,
    ProfileUpdate,
    ProfileListOut,
    ProfileOutAfterUpdate,
    ProfileDetailsOut
)
from .GENERAL import Message, Token


__all__ = [
    # User Schemas
    "UserCreate",
    "UserUpdate",
    "UpdatePassword",
    "SetPassword",
    "UserOut",
    "UserLoginRequest",
    "LoginSuccessfulData",
    "FollowCreate",
    "UnfollowOrRemoveFollowerSchema",
    "FollowerOrFollowingListOut",
    # Post & Tag Schemas
    "TagsIn",
    "PostCreate",
    "PostUpdate",
    "ChangePostPrivacy",
    "PostUpdateStatus",
    "TagOut",
    "PostOut",
    "PostListOut",
    "PostDetailsOut",
    "LikeUnlikePost",
    # Comment Schemas
    "CommentCreate",
    "CommentUpdate",
    "CommentOut",
    # List Schemas
    "ListCreate",
    "ListUpdate",
    "ListListOut",
    "ListDetailsOut",
    "SaveOrUnsavePost",
    "SaveOrUnsaveList",
    # Profile & Link Schemas
    "LinkCreate",
    "LinkUpdate",
    "LinkOut",
    "ProfileUpdate",
    "ProfileListOut",
    "ProfileOutAfterUpdate",
    "ProfileDetailsOut",
    # General schemas
    "Message",
    "Token",
]
