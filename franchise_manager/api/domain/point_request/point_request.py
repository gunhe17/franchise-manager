from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.point_request.amount import Amount
from franchise_manager.api.domain.point_request.method import Method
from franchise_manager.api.domain.point_request.status import Status
from franchise_manager.api.domain.point_request.decider_type import DeciderType
from franchise_manager.api.domain.point_request.requested_at import RequestedAt
from franchise_manager.api.domain.point_request.decided_at import DecidedAt
from franchise_manager.api.domain.point_request.memo import Memo


@dataclass(frozen=True, kw_only=True)
class PointRequest(Entity):
    user_id: UUID
    brand_id: UUID
    amount: Amount
    method: Method
    idempotency_key: UUID
    requested_at: RequestedAt
    status: Status
    decided_at: DecidedAt | None = None
    decided_by_type: DeciderType | None = None
    decided_by_id: UUID | None = None
    memo: Memo | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        user_id: UUID,
        brand_id: UUID,
        amount: Amount,
        method: Method,
        idempotency_key: UUID,
        requested_at: RequestedAt,
        status: Status,
        decided_at: DecidedAt | None = None,
        decided_by_type: DeciderType | None = None,
        decided_by_id: UUID | None = None,
        memo: Memo | None = None,
    ) -> "PointRequest":
        request = cls(
            user_id=user_id,
            brand_id=brand_id,
            amount=amount,
            method=method,
            idempotency_key=idempotency_key,
            requested_at=requested_at,
            status=status,
            decided_at=decided_at,
            decided_by_type=decided_by_type,
            decided_by_id=decided_by_id,
            memo=memo,
            by_factory=True,
        )
        return request

    # #
    # update

    def decide(
        self,
        *,
        status: Status,
        decided_at: DecidedAt,
        decided_by_type: DeciderType,
        decided_by_id: UUID,
        memo: Memo | None = None,
    ) -> "PointRequest":
        request = PointRequest(
            id=self.id,
            user_id=self.user_id,
            brand_id=self.brand_id,
            amount=self.amount,
            method=self.method,
            idempotency_key=self.idempotency_key,
            requested_at=self.requested_at,
            status=status,
            decided_at=decided_at,
            decided_by_type=decided_by_type,
            decided_by_id=decided_by_id,
            memo=memo,
            by_factory=True,
        )
        return request

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "brand_id": str(self.brand_id),
            "amount": self.amount.to_int(),
            "method": self.method.to_str(),
            "idempotency_key": str(self.idempotency_key),
            "requested_at": self.requested_at.to_str(),
            "status": self.status.to_str(),
            "decided_at": (
                self.decided_at.to_str() if self.decided_at else None
            ),
            "decided_by_type": (
                self.decided_by_type.to_str() if self.decided_by_type else None
            ),
            "decided_by_id": (
                str(self.decided_by_id) if self.decided_by_id else None
            ),
            "memo": (
                self.memo.to_str() if self.memo else None
            ),
        }

    def to_model(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "brand_id": self.brand_id,
            "amount": self.amount.to_int(),
            "method": self.method.to_str(),
            "idempotency_key": self.idempotency_key,
            "requested_at": self.requested_at.to_datetime(),
            "status": self.status.to_str(),
            "decided_at": (
                self.decided_at.to_datetime() if self.decided_at else None
            ),
            "decided_by_type": (
                self.decided_by_type.to_str() if self.decided_by_type else None
            ),
            "decided_by_id": self.decided_by_id,
            "memo": (
                self.memo.to_str() if self.memo else None
            ),
        }
