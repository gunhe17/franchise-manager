from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.brand.name import Name
from franchise_manager.api.domain.brand.business_number import BusinessNumber


@dataclass(frozen=True, kw_only=True)
class Brand(Entity):
    name: Name
    business_number: BusinessNumber | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        name: Name,
        business_number: BusinessNumber | None = None,
    ) -> "Brand":
        brand = cls(
            name=name,
            business_number=business_number,
            by_factory=True,
        )
        return brand

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name.to_str(),
            "business_number": self.business_number.to_str() if self.business_number else None,
        }

    def to_model(self):
        return {
            "id": self.id,
            "name": self.name.to_str(),
            "business_number": self.business_number.to_str() if self.business_number else None,
        }
