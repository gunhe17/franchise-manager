from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.audit_log.occurred_at import OccurredAt
from franchise_manager.api.domain.audit_log.actor_type import ActorType
from franchise_manager.api.domain.audit_log.action import Action
from franchise_manager.api.domain.audit_log.target_type import TargetType
from franchise_manager.api.domain.audit_log.target_id import TargetId
from franchise_manager.api.domain.audit_log.before import Before
from franchise_manager.api.domain.audit_log.after import After
from franchise_manager.api.domain.audit_log.context import Context
from franchise_manager.api.domain.audit_log.reason import Reason


@dataclass(frozen=True, kw_only=True)
class AuditLog(Entity):
    occurred_at: OccurredAt
    actor_type: ActorType
    actor_id: UUID | None
    action: Action
    target_type: TargetType
    target_id: TargetId
    request_id: UUID
    before: Before | None = None
    after: After | None = None
    reason: Reason | None = None
    context: Context | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        occurred_at: OccurredAt,
        actor_type: ActorType,
        actor_id: UUID | None,
        action: Action,
        target_type: TargetType,
        target_id: TargetId,
        request_id: UUID,
        before: Before | None = None,
        after: After | None = None,
        reason: Reason | None = None,
        context: Context | None = None,
    ) -> "AuditLog":
        log = cls(
            occurred_at=occurred_at,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            request_id=request_id,
            before=before,
            after=after,
            reason=reason,
            context=context,
            by_factory=True,
        )
        return log

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "occurred_at": self.occurred_at.to_str(),
            "actor_type": self.actor_type.to_str(),
            "actor_id": (
                str(self.actor_id) if self.actor_id else None
            ),
            "action": self.action.to_str(),
            "target_type": self.target_type.to_str(),
            "target_id": self.target_id.to_str(),
            "request_id": str(self.request_id),
            "before": (
                self.before.to_dict() if self.before else None
            ),
            "after": (
                self.after.to_dict() if self.after else None
            ),
            "reason": (
                self.reason.to_str() if self.reason else None
            ),
            "context": (
                self.context.to_dict() if self.context else None
            ),
        }

    def to_model(self):
        return {
            "id": self.id,
            "occurred_at": self.occurred_at.to_datetime(),
            "actor_type": self.actor_type.to_str(),
            "actor_id": self.actor_id,
            "action": self.action.to_str(),
            "target_type": self.target_type.to_str(),
            "target_id": self.target_id.to_str(),
            "request_id": self.request_id,
            "before": (
                self.before.to_dict() if self.before else None
            ),
            "after": (
                self.after.to_dict() if self.after else None
            ),
            "reason": (
                self.reason.to_str() if self.reason else None
            ),
            "context": (
                self.context.to_dict() if self.context else None
            ),
        }
