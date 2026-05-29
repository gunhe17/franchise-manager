from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, Integer, String, Uuid, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.point_request.point_request import PointRequest
from franchise_manager.api.domain.point_request.amount import Amount
from franchise_manager.api.domain.point_request.method import Method
from franchise_manager.api.domain.point_request.status import Status
from franchise_manager.api.domain.point_request.decider_type import DeciderType
from franchise_manager.api.domain.point_request.requested_at import RequestedAt
from franchise_manager.api.domain.point_request.decided_at import DecidedAt
from franchise_manager.api.domain.point_request.memo import Memo

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class PointRequestModel(Model):
    __tablename__ = "point_requests"

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
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    method: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    idempotency_key: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="pending",
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    decided_by_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    decided_by_id: Mapped[UUID | None] = mapped_column(
        Uuid,
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
            "uq_point_requests_idempotency_key",
            "idempotency_key",
            unique=True,
        ),
    )


# #
# mapper

def _to_point_request(model: PointRequestModel) -> PointRequest:
    request = PointRequest(
        id=model.id,
        user_id=model.user_id,
        brand_id=model.brand_id,
        amount=Amount.from_int(model.amount),
        method=Method.from_str(model.method),
        idempotency_key=model.idempotency_key,
        requested_at=RequestedAt.from_datetime(model.requested_at),
        status=Status.from_str(model.status),
        decided_at=DecidedAt.from_datetime(model.decided_at) if model.decided_at else None,
        decided_by_type=DeciderType.from_str(model.decided_by_type) if model.decided_by_type else None,
        decided_by_id=model.decided_by_id,
        memo=Memo.from_str(model.memo) if model.memo else None,
        by_factory=True,
    )
    return request


# #
# repository

class PointRequestRepository(PostgresRepository[PointRequest, PointRequestModel]):
    model = PointRequestModel
    mapper = _to_point_request

    # #
    # read

    async def find_by_user(
        self, *, session: AsyncSession, user_id: UUID
    ) -> list[PointRequest]:
        requests = await self._filter_by(session=session, column="user_id", value=user_id)
        return requests

    async def find_by_brand(
        self, *, session: AsyncSession, brand_id: UUID
    ) -> list[PointRequest]:
        requests = await self._filter_by(session=session, column="brand_id", value=brand_id)
        return requests


# #
# PointRequestRepository

point_request_repository = PointRequestRepository()  # type: ignore[call-arg]
