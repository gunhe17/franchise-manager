from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError, InvalidFormatError


@dataclass(frozen=True, kw_only=True)
class ReferenceType(ValueObject):
    _value: str

    # hint
    _allowed_list: tuple[str, ...] = ("order", "point_request", "adjustment")

    # #
    # factory

    @classmethod
    def from_str(cls, value) -> "ReferenceType":
        # type
        if not isinstance(value, str):
            raise InvalidError("ReferenceType")

        # format
        if value not in cls._allowed_list:
            raise InvalidFormatError("ReferenceType")

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_str(self) -> str:
        return self._value
