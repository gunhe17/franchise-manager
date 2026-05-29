from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError


@dataclass(frozen=True, kw_only=True)
class IsChecked(ValueObject):
    _value: bool

    # #
    # factory

    @classmethod
    def from_bool(cls, value) -> "IsChecked":
        # type
        if not isinstance(value, bool):
            raise InvalidError("IsChecked")

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_bool(self) -> bool:
        return self._value
