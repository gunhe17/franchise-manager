from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from franchise_manager.api.core.repository import Repository

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.model import Model

E = TypeVar("E", bound=Entity)
M = TypeVar("M", bound=Model)


class PostgresRepository(Repository, Generic[E, M]):
    def __init__(
        self,
        *,
        model: type[M],
        mapper: Callable[[M], E],
        entity: type[E] | None = None,
    ):
        self._model = model
        self._mapper = mapper
        self._entity = entity

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'model' in cls.__dict__ and 'mapper' in cls.__dict__:
            model_var = cls.__dict__['model']
            mapper_var = cls.__dict__['mapper']
            entity_var = cls.__dict__.get('entity', None)

            def __init__(self) -> None:
                PostgresRepository.__init__(self, model=model_var, mapper=mapper_var, entity=entity_var)

            cls.__init__ = __init__  # type: ignore[assignment]

    # #
    # create

    async def add(self, *, session: AsyncSession, entity: E) -> None:
        model = self._model(**entity.to_model())  # type: ignore[attr-defined]
        session.add(model)
        await session.flush()

    async def add_many(self, *, session: AsyncSession, entities: list[E]) -> None:
        if not entities:
            return
        models = [self._model(**e.to_model()) for e in entities]  # type: ignore[attr-defined]
        session.add_all(models)
        await session.flush()

    # #
    # read

    async def get_by_id(self, *, session: AsyncSession, id: UUID) -> E | None:
        model = await session.scalar(
            select(self._model).where(
                self._model.id == id,  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        if model is None:
            return None
        entity = self._mapper(model)
        return entity

    async def get_by_ids(self, *, session: AsyncSession, ids: list[UUID]) -> list[E]:
        result = await session.scalars(
            select(self._model).where(
                self._model.id.in_(ids),  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        entities = [self._mapper(m) for m in result]
        return entities

    async def exists_by_id(self, *, session: AsyncSession, id: UUID) -> bool:
        count = await session.scalar(
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

    async def update(self, *, session: AsyncSession, entity: E) -> None:
        payload = entity.to_model()  # type: ignore[attr-defined]
        id = payload.pop("id")
        await session.execute(
            sql_update(self._model)
            .where(
                self._model.id == id,  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .values(**payload, updated_at=func.now())
        )

    async def update_many(self, *, session: AsyncSession, entities: list[E]) -> None:
        for entity in entities:
            await self.update(session=session, entity=entity)

    # #
    # delete

    async def remove_by_id(self, *, session: AsyncSession, id: UUID) -> None:
        await session.execute(
            sql_update(self._model)
            .where(
                self._model.id == id,  # type: ignore[attr-defined]
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .values(deleted_at=func.now())
        )

    # #
    # finders
    # (subclass-domain methods like find_by_phone delegate to these)

    async def _find_by(self, *, session: AsyncSession, column: str, value: Any) -> E | None:
        col = getattr(self._model, column)
        model = await session.scalar(
            select(self._model).where(
                col == value,
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        if model is None:
            return None
        entity = self._mapper(model)
        return entity

    async def _filter_by(self, *, session: AsyncSession, column: str, value: Any) -> list[E]:
        col = getattr(self._model, column)
        result = await session.scalars(
            select(self._model).where(
                col == value,
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        entities = [self._mapper(m) for m in result]
        return entities

    async def _find_in(self, *, session: AsyncSession, column: str, values: list[Any]) -> list[E]:
        if not values:
            return []
        col = getattr(self._model, column)
        result = await session.scalars(
            select(self._model).where(
                col.in_(values),
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        entities = [self._mapper(m) for m in result]
        return entities

    async def _filter_by_all(self, *, session: AsyncSession, criteria: dict[str, Any]) -> list[E]:
        conditions = [getattr(self._model, column) == value for column, value in criteria.items()]
        result = await session.scalars(
            select(self._model).where(
                *conditions,
                self._model.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        entities = [self._mapper(m) for m in result]
        return entities

    # #
    # key-value
    # (subclass must wire `entity=` + model has `key` column + entity supports `new(key=, value=)` / `with_value(value)`)

    async def find_by_key(self, *, session: AsyncSession, key) -> E | None:
        entity = await self._find_by(session=session, column="key", value=key.to_str())
        return entity

    async def set_by_key(self, *, session: AsyncSession, key, value) -> None:
        existing = await self.find_by_key(session=session, key=key)
        if existing is None:
            await self.add(session=session, entity=self._entity.new(key=key, value=value))  # type: ignore[union-attr]
            return
        await self.update(session=session, entity=existing.with_value(value))  # type: ignore[attr-defined]

    async def set_by_keys(self, *, session: AsyncSession, pairs: list[tuple]) -> None:
        if not pairs:
            return
        # fetch existing
        existing = await self._find_in(
            session=session,
            column="key",
            values=[k.to_str() for k, _ in pairs],
        )
        existing_by_key = {e.key.to_str(): e for e in existing}  # type: ignore[attr-defined]
        # split
        to_add: list[E] = []
        to_update: list[E] = []
        for key, value in pairs:
            current = existing_by_key.get(key.to_str())
            if current is None:
                to_add.append(self._entity.new(key=key, value=value))  # type: ignore[union-attr]
            else:
                to_update.append(current.with_value(value))  # type: ignore[attr-defined]
        # write
        await self.add_many(session=session, entities=to_add)
        await self.update_many(session=session, entities=to_update)
