from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError, InvalidFormatError


@dataclass(frozen=True, kw_only=True)
class Amount(ValueObject):
    _value: int

    # #
    # factory

    @classmethod
    def from_int(cls, value) -> "Amount":
        # type
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidError("Amount")

        # range
        if value < 0:
            raise InvalidFormatError("Amount")

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_int(self) -> int:
        return self._value
