from .user_sch import (
    CreateUserSchema,
    UpdateUserSchema,
    UpdatePasswordSchema,
    SetNewPassword,
    UserLoginSchema,
    UserOutSchema,
    FollowOrUnfollowSchema,
    FollowerOrFollowingListSchema,
)
from .post_sch import (
    CreatePostSchema,
    UpdatePostSchema,
    ChangePostPrivacySchema,
    UpdatePostStatusSchema,
    ReadTagSchema,
    PostListSchema,
    PostDetailsSchema,
    LikeUnlikePostSchema
)
from .ticket_sch import CreateTicketSchema
from .comment_sch import (
    CreateCommentSchema,
    UpdateCommentContentSchema,
    UpdateCommentStatusSchema,
    CommentDetailsSchema
)
from .list_sch import (
    CreateListSchema,
    UpdateListSchema,
    ListListSchema,
    ListDetailsSchema,
    SaveOrUnsavePost,
    SaveOrUnsaveList
)
from .reports_sch import (
    CreateReportOnUserSchema,
    CreateReportOnPostSchema
)
from .profile_sch import (
    CreateLinkSchema,
    UpdateLinkSchema,
    LinkListSchema,
    InitialProfileSchema,
    UpdateProfileSchema,
    ProfileListSchema,
    ProfileDetailsSchema
)


__all__ = [
    # User Schemas
    "CreateUserSchema",
    "UpdateUserSchema",
    "UpdatePasswordSchema",
    "SetNewPassword",
    "UserLoginSchema",
    "UserOutSchema",
    "FollowOrUnfollowSchema",
    "FollowerOrFollowingListSchema",
    # Post & Tag Schemas
    "CreatePostSchema",
    "UpdatePostSchema",
    "ChangePostPrivacySchema",
    "UpdatePostStatusSchema",
    "ReadTagSchema",
    "PostListSchema",
    "PostDetailsSchema",
    "LikeUnlikePostSchema",
    # Ticket Schemas
    "CreateTicketSchema",
    # Comment Schemas
    "CreateCommentSchema",
    "UpdateCommentContentSchema",
    "UpdateCommentStatusSchema",
    "CommentDetailsSchema",
    # List Schemas
    "CreateListSchema",
    "UpdateListSchema",
    "ListListSchema",
    "ListDetailsSchema",
    "SaveOrUnsavePost",
    "SaveOrUnsaveList",
    # Reports (on users and posts) Schemas
    "CreateReportOnUserSchema",
    "CreateReportOnPostSchema",
    # Profile & Link Schemas
    "CreateLinkSchema",
    "UpdateLinkSchema",
    "LinkListSchema",
    "InitialProfileSchema",
    "UpdateProfileSchema",
    "ProfileListSchema",
    "ProfileDetailsSchema",
]
