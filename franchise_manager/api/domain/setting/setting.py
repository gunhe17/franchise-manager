from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.setting.key import Key
from franchise_manager.api.domain.setting.value import Value


@dataclass(frozen=True, kw_only=True)
class Setting(Entity):
    key: Key
    value: Value

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        key: Key,
        value: Value,
    ) -> "Setting":
        setting = cls(
            key=key,
            value=value,
            by_factory=True,
        )
        return setting

    # #
    # update

    def with_value(self, value: Value) -> "Setting":
        setting = Setting(id=self.id, key=self.key, value=value, by_factory=True)
        return setting

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "key": self.key.to_str(),
            "value": self.value.to_str(),
        }

    def to_model(self):
        return {
            "id": self.id,
            "key": self.key.to_str(),
            "value": self.value.to_str(),
        }
