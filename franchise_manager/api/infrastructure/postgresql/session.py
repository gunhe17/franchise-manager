from __future__ import annotations

from contextlib import asynccontextmanager

from franchise_manager.api.config import TestPostgresConfig
from franchise_manager.api.infrastructure.postgresql.client import Postgres, db_client


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
