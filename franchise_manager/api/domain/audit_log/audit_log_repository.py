from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.audit_log.audit_log import AuditLog
from franchise_manager.api.domain.audit_log.occurred_at import OccurredAt
from franchise_manager.api.domain.audit_log.actor_type import ActorType
from franchise_manager.api.domain.audit_log.action import Action
from franchise_manager.api.domain.audit_log.target_type import TargetType
from franchise_manager.api.domain.audit_log.target_id import TargetId
from franchise_manager.api.domain.audit_log.before import Before
from franchise_manager.api.domain.audit_log.after import After
from franchise_manager.api.domain.audit_log.context import Context
from franchise_manager.api.domain.audit_log.reason import Reason

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class AuditLogModel(Model):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    actor_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    actor_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        nullable=True,
    )
    action: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    target_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    target_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    request_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )
    before: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    after: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    context: Mapped[dict | None] = mapped_column(
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
# mapper

def _to_audit_log(model: AuditLogModel) -> AuditLog:
    log = AuditLog(
        id=model.id,
        occurred_at=OccurredAt.from_datetime(model.occurred_at),
        actor_type=ActorType.from_str(model.actor_type),
        actor_id=model.actor_id,
        action=Action.from_str(model.action),
        target_type=TargetType.from_str(model.target_type),
        target_id=TargetId.from_str(model.target_id),
        request_id=model.request_id,
        before=Before.from_dict(model.before) if model.before else None,
        after=After.from_dict(model.after) if model.after else None,
        reason=Reason.from_str(model.reason) if model.reason else None,
        context=Context.from_dict(model.context) if model.context else None,
        by_factory=True,
    )
    return log


# #
# repository

class AuditLogRepository(PostgresRepository[AuditLog, AuditLogModel]):
    model = AuditLogModel
    mapper = _to_audit_log

    # #
    # read

    async def find_by_action(
        self, *, session: AsyncSession, action: Action
    ) -> list[AuditLog]:
        logs = await self._filter_by(session=session, column="action", value=action.to_str())
        return logs

    async def find_by_target(
        self, *, session: AsyncSession, target_type: TargetType, target_id: TargetId
    ) -> list[AuditLog]:
        logs = await self._filter_by_all(
            session=session,
            criteria={
                "target_type": target_type.to_str(),
                "target_id": target_id.to_str(),
            },
        )
        return logs


# #
# AuditLogRepository

audit_log_repository = AuditLogRepository()  # type: ignore[call-arg]
