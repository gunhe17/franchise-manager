from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.store.code import Code
from franchise_manager.api.domain.store.name import Name
from franchise_manager.api.domain.store.address import Address


@dataclass(frozen=True, kw_only=True)
class Store(Entity):
    code: Code
    name: Name
    address: Address | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        code: Code,
        name: Name,
        address: Address | None = None,
    ) -> "Store":
        store = cls(
            code=code,
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
            "code": self.code.to_str(),
            "name": self.name.to_str(),
            "address": self.address.to_dict() if self.address else None,
        }

    def to_model(self):
        return {
            "id": self.id,
            "code": self.code.to_str(),
            "name": self.name.to_str(),
            "address": self.address.to_dict() if self.address else None,
        }
