from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, Integer, String, Uuid, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.order.order import Order
from franchise_manager.api.domain.order.external_order_number import ExternalOrderNumber
from franchise_manager.api.domain.order.amount import Amount
from franchise_manager.api.domain.order.attributes import Attributes
from franchise_manager.api.domain.order.ordered_at import OrderedAt
from franchise_manager.api.domain.order.received_at import ReceivedAt
from franchise_manager.api.domain.order.canceled_at import CanceledAt
from franchise_manager.api.domain.order.source import Source
from franchise_manager.api.domain.order.status import OrderStatus

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class OrderModel(Model):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    store_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )
    external_order_number: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    source: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="active",
    )
    attributes: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
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

    __table_args__ = (
        Index(
            "uq_orders_store_external_number_active",
            "store_id",
            "external_order_number",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


# #
# mapper

def _to_order(model: OrderModel) -> Order:
    order = Order(
        id=model.id,
        store_id=model.store_id,
        external_order_number=ExternalOrderNumber.from_str(model.external_order_number),
        ordered_at=OrderedAt.from_datetime(model.ordered_at),
        amount=Amount.from_int(model.amount),
        source=Source.from_str(model.source),
        received_at=ReceivedAt.from_datetime(model.received_at),
        status=OrderStatus.from_str(model.status),
        attributes=Attributes.from_dict(model.attributes) if model.attributes else None,
        canceled_at=CanceledAt.from_datetime(model.canceled_at) if model.canceled_at else None,
        by_factory=True,
    )
    return order


# #
# repository

class OrderRepository(PostgresRepository[Order, OrderModel]):
    model = OrderModel
    mapper = _to_order

    # #
    # read

    async def find_by_store(
        self, *, session: AsyncSession, store_id: UUID
    ) -> list[Order]:
        orders = await self._filter_by(session=session, column="store_id", value=store_id)
        return orders


# #
# OrderRepository

order_repository = OrderRepository()  # type: ignore[call-arg]
