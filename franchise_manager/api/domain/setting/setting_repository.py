from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.setting.setting import Setting
from franchise_manager.api.domain.setting.key import Key
from franchise_manager.api.domain.setting.value import Value

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class SettingModel(Model):
    __tablename__ = "settings"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    key: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    value: Mapped[str] = mapped_column(
        String,
        nullable=False,
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

    __table_args__ = (
        Index(
            "uq_settings_key_active",
            "key",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


# #
# mapper

def _to_setting(model: SettingModel) -> Setting:
    setting = Setting(
        id=model.id,
        key=Key.from_str(model.key),
        value=Value.from_str(model.value),
        by_factory=True,
    )
    return setting


# #
# repository

class SettingRepository(PostgresRepository[Setting, SettingModel]):
    model = SettingModel
    mapper = _to_setting
    entity = Setting


# #
# SettingRepository

setting_repository = SettingRepository()  # type: ignore[call-arg]
