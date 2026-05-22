from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from franchise_manager.api.config import TestPostgresConfig, get_postgres_config
from franchise_manager.api.core.model import Base

# register all models on Base.metadata (side-effect imports)
from franchise_manager.api.domain.brand.brand_repository import BrandModel  # pyright: ignore[reportUnusedImport]
from franchise_manager.api.domain.store.store_repository import StoreModel  # pyright: ignore[reportUnusedImport]
from franchise_manager.api.domain.user.user_repository import UserModel  # pyright: ignore[reportUnusedImport]


# #
# client

class Postgres:
    _tables_created = False

    def __init__(self, url: str):
        self.database_url = url
        self.engine: AsyncEngine = create_async_engine(
            self.database_url,
            echo=False,
        )
        self.SessionLocal = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False,
        )

    # #
    # ddl

    def _create_tables(self, conn):
        inspector = inspect(conn)
        existing = set(inspector.get_table_names())
        model_tables = set(Base.metadata.tables.keys())
        missing = model_tables - existing
        if missing:
            Base.metadata.create_all(conn)
            for t in missing:
                print(f"  + {t}")
        return len(missing)

    async def create_tables_once_in_process(self):
        if Postgres._tables_created:
            return
        print("Database: create_tables called")
        async with self.engine.begin() as conn:
            created = await conn.run_sync(self._create_tables)
        Postgres._tables_created = True
        print(f"Database: create_tables worked ({created} tables created)")

    async def delete_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self):
        await self.engine.dispose()


# #
# singleton

db_client = Postgres(get_postgres_config().database_url())


# #
# session

@asynccontextmanager
async def transactional_session(session_factory):
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def transactional_session_helper():
    await db_client.create_tables_once_in_process()
    async with transactional_session(db_client.SessionLocal) as session:
        yield session


# #
# test

@asynccontextmanager
async def transactional_test_session_helper():
    Postgres._tables_created = False
    test_client = Postgres(TestPostgresConfig().database_url())
    await test_client.create_tables_once_in_process()
    try:
        async with transactional_session(test_client.SessionLocal) as session:
            yield session
    finally:
        await test_client.delete_tables()
        await test_client.close()


# #
# cli

if __name__ == "__main__":
    import asyncio

    async def main():
        await db_client.create_tables_once_in_process()

    asyncio.run(main())
