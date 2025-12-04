"""
this package (src/schemas/admin/) includes admin-specific schemas.
(schemas which specifically is used for admin services, and
other users don't have access them)
"""

from .user import (
    UserUpdateForAdmin,
    UserListOut,
    UserOutForAdmin
)
from .post import (
    PostListOutForAdmin,
    PostDetailsOutForAdmin
)
from .ticket import (
    TicketListOut,
    TicketDetailsOut,
    TicketUpdateStatus
)
from .comment import CommentListOut
from .reports import (
    ReportOnUserListOut,
    ReportOnUserDetailsOut,
    ReportOnPostListOut,
    ReportOnPostDetailsOut
)
from .profile import (
    ProfileListOutForAdmin,
    ProfileDetailsOutForAdmin
)


__all__ = [
    # User Schemas
    "UserUpdateForAdmin",
    "UserListOut",
    "UserOutForAdmin",
    # Post
    "PostListOutForAdmin",
    "PostDetailsOutForAdmin",
    # Ticket
    "TicketListOut",
    "TicketDetailsOut",
    "TicketUpdateStatus",
    # Comment
    "CommentListOut",
    # Reports (on users and posts)
    "ReportOnUserListOut",
    "ReportOnUserDetailsOut",
    "ReportOnPostListOut",
    "ReportOnPostDetailsOut",
    # Profile
    "ProfileListOutForAdmin",
    "ProfileDetailsOutForAdmin"
]
