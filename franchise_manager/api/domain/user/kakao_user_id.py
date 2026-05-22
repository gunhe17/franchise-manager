from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject


@dataclass(frozen=True, kw_only=True)
class KakaoUserId(ValueObject):
    _value: str

    # #
    # factory

    @classmethod
    def from_str(cls, value) -> "KakaoUserId":
        # type
        if not isinstance(value, str):
            raise  # InvalidError

        # value
        if not value.strip():
            raise  # InvalidFormatError

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_str(self) -> str:
        return self._value
