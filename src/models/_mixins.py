"""
in this module: there are some MixinClasses to add some extra features
to SqlAlchemy models, or to centralize common features of them at one place.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtFieldMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )


class UpdateAtFieldMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )
