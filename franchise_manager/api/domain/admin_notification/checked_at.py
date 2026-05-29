from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError


@dataclass(frozen=True, kw_only=True)
class CheckedAt(ValueObject):
    _value: datetime

    # #
    # factory

    @classmethod
    def from_datetime(cls, value) -> "CheckedAt":
        # type
        if not isinstance(value, datetime):
            raise InvalidError("CheckedAt")

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_str(self) -> str:
        return self._value.isoformat()

    def to_datetime(self) -> datetime:
        return self._value
