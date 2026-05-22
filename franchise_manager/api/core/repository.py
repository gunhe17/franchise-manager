from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID


T = TypeVar("T")


class Repository(ABC, Generic[T]):
    # #
    # create

    @abstractmethod
    async def add(self, entity: T) -> None:
        ...

    # #
    # read

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        ...

    @abstractmethod
    async def get_by_ids(self, ids: list[UUID]) -> list[T]:
        ...

    @abstractmethod
    async def exists_by_id(self, id: UUID) -> bool:
        ...

    # #
    # update

    @abstractmethod
    async def update(self, entity: T) -> None:
        ...

    # #
    # delete

    @abstractmethod
    async def remove_by_id(self, id: UUID) -> None:
        ...
