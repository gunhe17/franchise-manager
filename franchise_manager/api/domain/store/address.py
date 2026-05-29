from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject
from franchise_manager.api.domain.common.exception import InvalidError, InvalidFormatError


@dataclass(frozen=True, kw_only=True)
class Address(ValueObject):
    _text: str
    _latitude: float
    _longitude: float
    _road_address: str | None = None
    _postal_code: str | None = None

    # #
    # factory

    @classmethod
    def from_dict(cls, value) -> "Address":
        # type
        if not isinstance(value, dict):
            raise InvalidError("Address")

        # components
        text = value.get("text")
        latitude = value.get("latitude")
        longitude = value.get("longitude")
        road_address = value.get("road_address")
        postal_code = value.get("postal_code")

        # required
        if not isinstance(text, str) or not text.strip():
            raise InvalidFormatError("Address.text")
        if not isinstance(latitude, (int, float)):
            raise InvalidFormatError("Address.latitude")
        if not isinstance(longitude, (int, float)):
            raise InvalidFormatError("Address.longitude")

        # range
        if not (-90.0 <= float(latitude) <= 90.0):
            raise InvalidFormatError("Address.latitude (range)")
        if not (-180.0 <= float(longitude) <= 180.0):
            raise InvalidFormatError("Address.longitude (range)")

        # optional
        if road_address is not None and not isinstance(road_address, str):
            raise InvalidFormatError("Address.road_address")
        if postal_code is not None and not isinstance(postal_code, str):
            raise InvalidFormatError("Address.postal_code")

        return cls(
            _text=text,
            _latitude=float(latitude),
            _longitude=float(longitude),
            _road_address=road_address,
            _postal_code=postal_code,
            by_factory=True,
        )

    # #
    # query

    def to_dict(self) -> dict:
        result: dict = {
            "text": self._text,
            "latitude": self._latitude,
            "longitude": self._longitude,
        }
        if self._road_address is not None:
            result["road_address"] = self._road_address
        if self._postal_code is not None:
            result["postal_code"] = self._postal_code
        return result
