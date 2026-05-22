from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Base
from franchise_manager.api.core.repository import Repository

from franchise_manager.api.domain.brand.brand import Brand


# #
# model

class BrandModel(Base):
    __tablename__ = "brands"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    business_number: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


# #
# repository

class BrandRepository(Repository[Brand]):
    ...
