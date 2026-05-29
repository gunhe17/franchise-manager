from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.store.name import Name
from franchise_manager.api.domain.store.address import Address


@dataclass(frozen=True, kw_only=True)
class Store(Entity):
    name: Name
    address: Address | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        name: Name,
        address: Address | None = None,
    ) -> "Store":
        store = cls(
            name=name,
            address=address,
            by_factory=True,
        )
        return store

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name.to_str(),
            "address": (
                self.address.to_dict() if self.address else None
            ),
        }

    def to_model(self):
        return {
            "id": self.id,
            "name": self.name.to_str(),
            "address": (
                self.address.to_dict() if self.address else None
            ),
        }
