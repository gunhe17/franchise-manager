from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Uuid, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.admin_notification.admin_notification import AdminNotification
from franchise_manager.api.domain.admin_notification.is_checked import IsChecked
from franchise_manager.api.domain.admin_notification.checked_at import CheckedAt

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class AdminNotificationModel(Model):
    __tablename__ = "admin_notifications"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    audit_log_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
        unique=True,  # 영구 1:1 — 알림은 처리(soft-delete) 후 재생성하지 않으므로 partial 아님
    )
    is_checked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
# mapper

def _to_admin_notification(model: AdminNotificationModel) -> AdminNotification:
    notification = AdminNotification(
        id=model.id,
        audit_log_id=model.audit_log_id,
        is_checked=IsChecked.from_bool(model.is_checked),
        checked_at=CheckedAt.from_datetime(model.checked_at) if model.checked_at else None,
        by_factory=True,
    )
    return notification


# #
# repository

class AdminNotificationRepository(PostgresRepository[AdminNotification, AdminNotificationModel]):
    model = AdminNotificationModel
    mapper = _to_admin_notification

    # #
    # read

    async def find_unchecked(
        self, *, session: AsyncSession
    ) -> list[AdminNotification]:
        notifications = await self._filter_by(
            session=session, column="is_checked", value=False
        )
        return notifications


# #
# AdminNotificationRepository

admin_notification_repository = AdminNotificationRepository()  # type: ignore[call-arg]
