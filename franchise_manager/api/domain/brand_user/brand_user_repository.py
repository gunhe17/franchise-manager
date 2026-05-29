from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.brand_user.brand_user import BrandUser
from franchise_manager.api.domain.brand_user.effective_from import EffectiveFrom
from franchise_manager.api.domain.brand_user.effective_to import EffectiveTo

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class BrandUserModel(Model):
    __tablename__ = "brand_users"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
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

def _to_brand_user(model: BrandUserModel) -> BrandUser:
    brand_user = BrandUser(
        id=model.id,
        user_id=model.user_id,
        brand_id=model.brand_id,
        effective_from=EffectiveFrom.from_datetime(model.effective_from),
        effective_to=EffectiveTo.from_datetime(model.effective_to) if model.effective_to else None,
        by_factory=True,
    )
    return brand_user


# #
# repository

class BrandUserRepository(PostgresRepository[BrandUser, BrandUserModel]):
    model = BrandUserModel
    mapper = _to_brand_user

    # #
    # read

    async def filter_by_user(
        self, *, session: AsyncSession, user_id: UUID
    ) -> list[BrandUser]:
        brand_users = await self._filter_by(session=session, column="user_id", value=user_id)
        return brand_users

    async def filter_by_brand(
        self, *, session: AsyncSession, brand_id: UUID
    ) -> list[BrandUser]:
        brand_users = await self._filter_by(session=session, column="brand_id", value=brand_id)
        return brand_users


# #
# BrandUserRepository

brand_user_repository = BrandUserRepository()  # type: ignore[call-arg]
