from .user_sch import (
    CreateUserSchema,
    UpdateUserSchema,
    UpdateUserForAdminSchema,
    UpdatePasswordSchema,
    SetNewPassword,
)
from .post_sch import (
    CreateTagSchema,
    ReadTagSchema,
    CreatePostSchema,
    UpdatePostSchema,
    ChangePostPrivacySchema,
    UpdatePostStatusSchema
)
from .ticket_sch import (
    CreateTicketSchema,
    UpdateTicketStatusForAdminSchema,
    TicketListSchema,
    TicketDetailsSchema
)
from .comment_sch import (
    CreateCommentSchema,
    UpdateCommentContentSchema,
    UpdateCommentStatusSchema,
    CommentListSchema,
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


__all__ = [
    # User Schemas
    "CreateUserSchema",
    "UpdateUserSchema",
    "UpdateUserForAdminSchema",
    "UpdatePasswordSchema",
    "SetNewPassword",
    # Post & Tag Schemas
    "CreateTagSchema",
    "ReadTagSchema",
    "CreatePostSchema",
    "UpdatePostSchema",
    "ChangePostPrivacySchema",
    "UpdatePostStatusSchema",
    # Ticket Schemas
    "CreateTicketSchema",
    "UpdateTicketStatusForAdminSchema",
    "TicketListSchema",
    "TicketDetailsSchema",
    # Comment Schemas
    "CreateCommentSchema",
    "UpdateCommentContentSchema",
    "UpdateCommentStatusSchema",
    "CommentListSchema",
    "CommentDetailsSchema",
    # List Schemas
    "CreateListSchema",
    "UpdateListSchema",
    "ListListSchema",
    "ListDetailsSchema",
    "SaveOrUnsavePost",
    "SaveOrUnsaveList",
]
