from __future__ import annotations

import re
from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject


@dataclass(frozen=True, kw_only=True)
class Phone(ValueObject):
    _value: str

    # #
    # factory

    @classmethod
    def from_str(cls, value) -> "Phone":
        # type
        if not isinstance(value, str):
            raise  # InvalidError

        # format
        if not re.match(r"^\+[1-9]\d{6,14}$", value):
            raise  # InvalidFormatError

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_str(self) -> str:
        return self._value
