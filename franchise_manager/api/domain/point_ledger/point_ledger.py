from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.point_ledger.delta import Delta
from franchise_manager.api.domain.point_ledger.point_type import PointType
from franchise_manager.api.domain.point_ledger.reference_type import ReferenceType
from franchise_manager.api.domain.point_ledger.idempotency_key import IdempotencyKey
from franchise_manager.api.domain.point_ledger.memo import Memo


@dataclass(frozen=True, kw_only=True)
class PointLedger(Entity):
    brand_id: UUID
    delta: Delta
    type: PointType
    reference_type: ReferenceType | None = None
    reference_id: UUID | None = None
    idempotency_key: IdempotencyKey | None = None
    memo: Memo | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        brand_id: UUID,
        delta: Delta,
        type: PointType,
        reference_type: ReferenceType | None = None,
        reference_id: UUID | None = None,
        idempotency_key: IdempotencyKey | None = None,
        memo: Memo | None = None,
    ) -> "PointLedger":
        ledger = cls(
            brand_id=brand_id,
            delta=delta,
            type=type,
            reference_type=reference_type,
            reference_id=reference_id,
            idempotency_key=idempotency_key,
            memo=memo,
            by_factory=True,
        )
        return ledger

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "brand_id": str(self.brand_id),
            "delta": self.delta.to_int(),
            "type": self.type.to_str(),
            "reference_type": (
                self.reference_type.to_str() if self.reference_type else None
            ),
            "reference_id": (
                str(self.reference_id) if self.reference_id else None
            ),
            "idempotency_key": (
                self.idempotency_key.to_str() if self.idempotency_key else None
            ),
            "memo": (
                self.memo.to_str() if self.memo else None
            ),
        }

    def to_model(self):
        return {
            "id": self.id,
            "brand_id": self.brand_id,
            "delta": self.delta.to_int(),
            "type": self.type.to_str(),
            "reference_type": (
                self.reference_type.to_str() if self.reference_type else None
            ),
            "reference_id": self.reference_id,
            "idempotency_key": (
                self.idempotency_key.to_str() if self.idempotency_key else None
            ),
            "memo": (
                self.memo.to_str() if self.memo else None
            ),
        }
