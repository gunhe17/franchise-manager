from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError, InvalidFormatError


@dataclass(frozen=True, kw_only=True)
class RefreshToken(ValueObject):
    _value: str

    # #
    # factory

    @classmethod
    def from_str(cls, value) -> "RefreshToken":
        # type
        if not isinstance(value, str):
            raise InvalidError("RefreshToken")

        # format
        # TODO: 발급 스킴(opaque base64url vs JWT) 확정 후 charset·length 검증 강화
        if not value.strip():
            raise InvalidFormatError("RefreshToken")

        return cls(_value=value, by_factory=True)

    # #
    # query

    def to_str(self) -> str:
        return self._value
