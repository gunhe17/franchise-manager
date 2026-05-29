from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError


@dataclass(frozen=True, kw_only=True)
class Before(ValueObject):
    _value: dict

    # #
    # factory

    @classmethod
    def from_dict(cls, value) -> "Before":
        # type
        if not isinstance(value, dict):
            raise InvalidError("Before")

        return cls(_value=dict(value), by_factory=True)

    # #
    # query

    def to_dict(self) -> dict:
        return dict(self._value)
