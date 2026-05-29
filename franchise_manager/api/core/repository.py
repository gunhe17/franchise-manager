from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class Repository(ABC):
    # #
    # create

    @abstractmethod
    async def add(self, *, session: AsyncSession, entity: Any) -> None:
        ...

    @abstractmethod
    async def add_many(self, *, session: AsyncSession, entities: list[Any]) -> None:
        ...

    # #
    # read

    @abstractmethod
    async def get_by_id(self, *, session: AsyncSession, id: UUID) -> Any | None:
        ...

    @abstractmethod
    async def get_by_ids(self, *, session: AsyncSession, ids: list[UUID]) -> list[Any]:
        ...

    @abstractmethod
    async def exists_by_id(self, *, session: AsyncSession, id: UUID) -> bool:
        ...

    # #
    # update

    @abstractmethod
    async def update(self, *, session: AsyncSession, entity: Any) -> None:
        ...

    @abstractmethod
    async def update_many(self, *, session: AsyncSession, entities: list[Any]) -> None:
        ...

    # #
    # delete

    @abstractmethod
    async def remove_by_id(self, *, session: AsyncSession, id: UUID) -> None:
        ...
