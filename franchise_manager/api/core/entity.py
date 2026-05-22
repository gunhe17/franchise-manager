from __future__ import annotations

import uuid
from dataclasses import InitVar, dataclass, field


@dataclass(frozen=True, kw_only=True)
class Entity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    by_factory: InitVar[bool] = False

    def __post_init__(self, by_factory: bool):
        if not by_factory:
            raise  # Error
