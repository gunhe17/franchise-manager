from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError, InvalidFormatError


@dataclass(frozen=True, kw_only=True)
class ExternalOrderNumber(ValueObject):
    _value: str

    # #
    # factory

    @classmethod
    def from_str(cls, value) -> "ExternalOrderNumber":
        # type
        if not isinstance(value, str):
            raise InvalidError("ExternalOrderNumber")

        # format
        if not value.strip():
            raise InvalidFormatError("ExternalOrderNumber")

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_str(self) -> str:
        return self._value
