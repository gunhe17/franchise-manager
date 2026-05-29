from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.admin_notification.is_checked import IsChecked
from franchise_manager.api.domain.admin_notification.checked_at import CheckedAt


@dataclass(frozen=True, kw_only=True)
class AdminNotification(Entity):
    audit_log_id: UUID
    is_checked: IsChecked
    checked_at: CheckedAt | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        audit_log_id: UUID,
        is_checked: IsChecked | None = None,
        checked_at: CheckedAt | None = None,
    ) -> "AdminNotification":
        notification = cls(
            audit_log_id=audit_log_id,
            is_checked=is_checked if is_checked is not None else IsChecked.from_bool(False),
            checked_at=checked_at,
            by_factory=True,
        )
        return notification

    # #
    # update

    def with_checked(self, checked_at: CheckedAt) -> "AdminNotification":
        notification = AdminNotification(
            id=self.id,
            audit_log_id=self.audit_log_id,
            is_checked=IsChecked.from_bool(True),
            checked_at=checked_at,
            by_factory=True,
        )
        return notification

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "audit_log_id": str(self.audit_log_id),
            "is_checked": self.is_checked.to_bool(),
            "checked_at": (
                self.checked_at.to_str() if self.checked_at else None
            ),
        }

    def to_model(self):
        return {
            "id": self.id,
            "audit_log_id": self.audit_log_id,
            "is_checked": self.is_checked.to_bool(),
            "checked_at": (
                self.checked_at.to_datetime() if self.checked_at else None
            ),
        }
