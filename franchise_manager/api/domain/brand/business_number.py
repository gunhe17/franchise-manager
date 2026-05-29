from __future__ import annotations

import re
from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError, InvalidFormatError


@dataclass(frozen=True, kw_only=True)
class BusinessNumber(ValueObject):
    _value: str

    # #
    # factory

    @classmethod
    def from_str(cls, value) -> "BusinessNumber":
        # type
        if not isinstance(value, str):
            raise InvalidError("BusinessNumber")

        # format
        if not re.match(r"^\d{3}-\d{2}-\d{5}$", value):
            raise InvalidFormatError("BusinessNumber")

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_str(self) -> str:
        return self._value
