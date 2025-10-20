"""
this package (src/schemas/admin/) includes admin-specific schemas.
(schemas which specifically is used for admin services, and
other users don't have access them)
"""

from .user import (
    UpdateUserForAdminSchema,
    UserListSchema,
    UserDetailsForAdminSchema
)
from .post import (
    PostListForAdminSchema,
    PostDetailsForAdminSchema
)
from .ticket import (
    TicketListSchema,
    TicketDetailsSchema,
    UpdateTicketStatusSchema
)
from .comment import CommentListSchema
from .reports import (
    ReportOnUserListSchema,
    ReportOnUserDetailsSchema,
    ReportOnPostListSchema,
    ReportOnPostDetailsSchema
)
from .profile import (
    ProfileListForAdminPanelSchema,
    ProfileDetailsForAdminPanelSchema
)


__all__ = [
    # User Schemas
    "UpdateUserForAdminSchema",
    "UserListSchema",
    "UserDetailsForAdminSchema",
    # Post
    "PostListForAdminSchema",
    "PostDetailsForAdminSchema",
    # Ticket
    "TicketListSchema",
    "TicketDetailsSchema",
    "UpdateTicketStatusSchema",
    # Comment
    "CommentListSchema",
    # Reports (on users and posts)
    "ReportOnUserListSchema",
    "ReportOnUserDetailsSchema",
    "ReportOnPostListSchema",
    "ReportOnPostDetailsSchema",
    # Profile
    "ProfileListForAdminPanelSchema",
    "ProfileDetailsForAdminPanelSchema"
]
