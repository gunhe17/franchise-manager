from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Base
from franchise_manager.api.core.repository import Repository

from franchise_manager.api.domain.store.store import Store
from franchise_manager.api.domain.store.code import Code
from franchise_manager.api.domain.store.name import Name


# #
# model

class StoreModel(Base):
    __tablename__ = "stores"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    code: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    address: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


# #
# repository

class StoreRepository(Repository[Store]):
    # #
    # read

    @abstractmethod
    async def find_by_code(self, code: Code) -> Store | None:
        ...

    @abstractmethod
    async def get_filtered_by_name(self, name: Name) -> list[Store]:
        ...
