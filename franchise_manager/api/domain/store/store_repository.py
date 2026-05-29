from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.store.store import Store
from franchise_manager.api.domain.store.name import Name
from franchise_manager.api.domain.store.address import Address

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class StoreModel(Model):
    __tablename__ = "stores"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    address: Mapped[dict | None] = mapped_column(
        JSONB,
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

def _to_store(model: StoreModel) -> Store:
    store = Store(
        id=model.id,
        name=Name.from_str(model.name),
        address=Address.from_dict(model.address) if model.address else None,
        by_factory=True,
    )
    return store


# #
# repository

class StoreRepository(PostgresRepository[Store, StoreModel]):
    model = StoreModel
    mapper = _to_store

    # #
    # read

    async def filter_by_name(self, *, session: AsyncSession, name: Name) -> list[Store]:
        stores = await self._filter_by(session=session, column="name", value=name.to_str())
        return stores


# #
# StoreRepository

store_repository = StoreRepository()  # type: ignore[call-arg]
