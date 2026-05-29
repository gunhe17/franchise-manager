from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.brand_user.effective_from import EffectiveFrom
from franchise_manager.api.domain.brand_user.effective_to import EffectiveTo


@dataclass(frozen=True, kw_only=True)
class BrandUser(Entity):
    user_id: UUID
    brand_id: UUID
    effective_from: EffectiveFrom
    effective_to: EffectiveTo | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        user_id: UUID,
        brand_id: UUID,
        effective_from: EffectiveFrom,
        effective_to: EffectiveTo | None = None,
    ) -> "BrandUser":
        brand_user = cls(
            user_id=user_id,
            brand_id=brand_id,
            effective_from=effective_from,
            effective_to=effective_to,
            by_factory=True,
        )
        return brand_user

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "brand_id": str(self.brand_id),
            "effective_from": self.effective_from.to_str(),
            "effective_to": (
                self.effective_to.to_str() if self.effective_to else None
            ),
        }

    def to_model(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "brand_id": self.brand_id,
            "effective_from": self.effective_from.to_datetime(),
            "effective_to": (
                self.effective_to.to_datetime() if self.effective_to else None
            ),
        }
