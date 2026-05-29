from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, Integer, String, Uuid, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.point_ledger.point_ledger import PointLedger
from franchise_manager.api.domain.point_ledger.delta import Delta
from franchise_manager.api.domain.point_ledger.point_type import PointType
from franchise_manager.api.domain.point_ledger.reference_type import ReferenceType
from franchise_manager.api.domain.point_ledger.idempotency_key import IdempotencyKey
from franchise_manager.api.domain.point_ledger.memo import Memo

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class PointLedgerModel(Model):
    __tablename__ = "point_ledgers"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    brand_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )
    delta: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    reference_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    reference_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        nullable=True,
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    memo: Mapped[str | None] = mapped_column(
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
            "uq_point_ledgers_idempotency_key",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        ),
    )


# #
# mapper

def _to_point_ledger(model: PointLedgerModel) -> PointLedger:
    ledger = PointLedger(
        id=model.id,
        brand_id=model.brand_id,
        delta=Delta.from_int(model.delta),
        type=PointType.from_str(model.type),
        reference_type=ReferenceType.from_str(model.reference_type) if model.reference_type else None,
        reference_id=model.reference_id,
        idempotency_key=IdempotencyKey.from_str(model.idempotency_key) if model.idempotency_key else None,
        memo=Memo.from_str(model.memo) if model.memo else None,
        by_factory=True,
    )
    return ledger


# #
# repository

class PointLedgerRepository(PostgresRepository[PointLedger, PointLedgerModel]):
    model = PointLedgerModel
    mapper = _to_point_ledger

    # #
    # read

    async def find_by_brand(
        self, *, session: AsyncSession, brand_id: UUID
    ) -> list[PointLedger]:
        ledgers = await self._filter_by(session=session, column="brand_id", value=brand_id)
        return ledgers


# #
# PointLedgerRepository

point_ledger_repository = PointLedgerRepository()  # type: ignore[call-arg]
