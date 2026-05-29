from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.order.external_order_number import ExternalOrderNumber
from franchise_manager.api.domain.order.amount import Amount
from franchise_manager.api.domain.order.attributes import Attributes
from franchise_manager.api.domain.order.ordered_at import OrderedAt
from franchise_manager.api.domain.order.received_at import ReceivedAt
from franchise_manager.api.domain.order.canceled_at import CanceledAt
from franchise_manager.api.domain.order.source import Source
from franchise_manager.api.domain.order.status import OrderStatus


@dataclass(frozen=True, kw_only=True)
class Order(Entity):
    store_id: UUID
    external_order_number: ExternalOrderNumber
    ordered_at: OrderedAt
    amount: Amount
    source: Source
    received_at: ReceivedAt
    status: OrderStatus
    attributes: Attributes | None = None
    canceled_at: CanceledAt | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        store_id: UUID,
        external_order_number: ExternalOrderNumber,
        ordered_at: OrderedAt,
        amount: Amount,
        source: Source,
        received_at: ReceivedAt,
        status: OrderStatus,
        attributes: Attributes | None = None,
        canceled_at: CanceledAt | None = None,
    ) -> "Order":
        order = cls(
            store_id=store_id,
            external_order_number=external_order_number,
            ordered_at=ordered_at,
            amount=amount,
            source=source,
            received_at=received_at,
            status=status,
            attributes=attributes,
            canceled_at=canceled_at,
            by_factory=True,
        )
        return order

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "store_id": str(self.store_id),
            "external_order_number": self.external_order_number.to_str(),
            "ordered_at": self.ordered_at.to_str(),
            "amount": self.amount.to_int(),
            "source": self.source.to_str(),
            "received_at": self.received_at.to_str(),
            "status": self.status.to_str(),
            "attributes": (
                self.attributes.to_dict() if self.attributes else None
            ),
            "canceled_at": (
                self.canceled_at.to_str() if self.canceled_at else None
            ),
        }

    def to_model(self):
        return {
            "id": self.id,
            "store_id": self.store_id,
            "external_order_number": self.external_order_number.to_str(),
            "ordered_at": self.ordered_at.to_datetime(),
            "amount": self.amount.to_int(),
            "source": self.source.to_str(),
            "received_at": self.received_at.to_datetime(),
            "status": self.status.to_str(),
            "attributes": (
                self.attributes.to_dict() if self.attributes else None
            ),
            "canceled_at": (
                self.canceled_at.to_datetime() if self.canceled_at else None
            ),
        }
