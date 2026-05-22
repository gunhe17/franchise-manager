from __future__ import annotations

from typing import Callable, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from franchise_manager.api.core.repository import Repository


TEntity = TypeVar("TEntity")
TModel = TypeVar("TModel")


class PostgresRepository(Repository[TEntity], Generic[TEntity, TModel]):
    def __init__(
        self,
        *,
        session: AsyncSession,
        model: type[TModel],
        mapper: Callable[[TModel], TEntity],
    ):
        self._session = session
        self._model = model
        self._mapper = mapper

    # #
    # create

    async def add(self, entity: TEntity) -> None:
        model = self._model(**entity.to_model())  # type: ignore[attr-defined]
        self._session.add(model)
        await self._session.flush()

    # #
    # read

    async def get_by_id(self, id: UUID) -> TEntity | None:
        model = await self._session.scalar(
            select(self._model).where(
                self._model.id == id,  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        if model is None:
            return None
        entity = self._mapper(model)
        return entity

    async def get_by_ids(self, ids: list[UUID]) -> list[TEntity]:
        result = await self._session.scalars(
            select(self._model).where(
                self._model.id.in_(ids),  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        entities = [self._mapper(m) for m in result]
        return entities

    async def exists_by_id(self, id: UUID) -> bool:
        count = await self._session.scalar(
            select(func.count())
            .select_from(self._model)
            .where(
                self._model.id == id,  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        exists = (count or 0) > 0
        return exists

    # #
    # update

    async def update(self, entity: TEntity) -> None:
        payload = entity.to_model()  # type: ignore[attr-defined]
        id = payload.pop("id")
        await self._session.execute(
            sql_update(self._model)
            .where(
                self._model.id == id,  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .values(**payload, updated_at=func.now())
        )

    # #
    # delete

    async def remove_by_id(self, id: UUID) -> None:
        await self._session.execute(
            sql_update(self._model)
            .where(
                self._model.id == id,  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .values(deleted_at=func.now())
        )
