from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.value_object import ValueObject


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
            raise  # InvalidError

        # components
        text = value.get("text")
        latitude = value.get("latitude")
        longitude = value.get("longitude")
        road_address = value.get("road_address")
        postal_code = value.get("postal_code")

        # required
        if not isinstance(text, str) or not text.strip():
            raise  # InvalidFormatError
        if not isinstance(latitude, (int, float)):
            raise  # InvalidFormatError
        if not isinstance(longitude, (int, float)):
            raise  # InvalidFormatError

        # range
        if not (-90.0 <= float(latitude) <= 90.0):
            raise  # InvalidFormatError
        if not (-180.0 <= float(longitude) <= 180.0):
            raise  # InvalidFormatError

        # optional
        if road_address is not None and not isinstance(road_address, str):
            raise  # InvalidFormatError
        if postal_code is not None and not isinstance(postal_code, str):
            raise  # InvalidFormatError

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
