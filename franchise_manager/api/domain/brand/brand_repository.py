from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.brand.brand import Brand
from franchise_manager.api.domain.brand.name import Name
from franchise_manager.api.domain.brand.business_number import BusinessNumber

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class BrandModel(Model):
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

    __table_args__ = (
        Index(
            "uq_brands_business_number_active",
            "business_number",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND business_number IS NOT NULL"),
        ),
    )


# #
# mapper

def _to_brand(model: BrandModel) -> Brand:
    brand = Brand(
        id=model.id,
        name=Name.from_str(model.name),
        business_number=(
            BusinessNumber.from_str(model.business_number) if model.business_number else None
        ),
        by_factory=True,
    )
    return brand


# #
# repository

class BrandRepository(PostgresRepository[Brand, BrandModel]):
    model = BrandModel
    mapper = _to_brand


# #
# BrandRepository

brand_repository = BrandRepository()  # type: ignore[call-arg]