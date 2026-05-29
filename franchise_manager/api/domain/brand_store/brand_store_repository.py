from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.brand_store.brand_store import BrandStore
from franchise_manager.api.domain.brand_store.effective_from import EffectiveFrom
from franchise_manager.api.domain.brand_store.effective_to import EffectiveTo

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class BrandStoreModel(Model):
    __tablename__ = "brand_stores"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    store_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )
    brand_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
# mapper

def _to_brand_store(model: BrandStoreModel) -> BrandStore:
    brand_store = BrandStore(
        id=model.id,
        store_id=model.store_id,
        brand_id=model.brand_id,
        effective_from=EffectiveFrom.from_datetime(model.effective_from),
        effective_to=EffectiveTo.from_datetime(model.effective_to) if model.effective_to else None,
        by_factory=True,
    )
    return brand_store


# #
# repository

class BrandStoreRepository(PostgresRepository[BrandStore, BrandStoreModel]):
    model = BrandStoreModel
    mapper = _to_brand_store

    # #
    # read

    async def filter_by_store(
        self, *, session: AsyncSession, store_id: UUID
    ) -> list[BrandStore]:
        brand_stores = await self._filter_by(session=session, column="store_id", value=store_id)
        return brand_stores

    async def filter_by_brand(
        self, *, session: AsyncSession, brand_id: UUID
    ) -> list[BrandStore]:
        brand_stores = await self._filter_by(session=session, column="brand_id", value=brand_id)
        return brand_stores


# #
# BrandStoreRepository

brand_store_repository = BrandStoreRepository()  # type: ignore[call-arg]
