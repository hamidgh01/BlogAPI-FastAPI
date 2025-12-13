"""
this package (src/routes/admin/) includes admin-specific routes.
(routes which specifically is used for admin services, and
other users don't have access them)
"""

from ._admin_router import admin_router
from . import post, comment


__all__ = ["admin_router"]
