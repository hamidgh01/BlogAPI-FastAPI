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
from .comment import CommentListOut
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
    # Comment
    "CommentListOut",
    # Profile
    "ProfileListOutForAdmin",
    "ProfileDetailsOutForAdmin"
]
