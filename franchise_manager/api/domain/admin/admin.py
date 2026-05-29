from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.admin.email import Email
from franchise_manager.api.domain.admin.name import Name
from franchise_manager.api.domain.admin.password import Password
from franchise_manager.api.domain.admin.role import Role
from franchise_manager.api.domain.admin.refresh_token import RefreshToken


@dataclass(frozen=True, kw_only=True)
class Admin(Entity):
    email: Email
    password: Password
    name: Name
    role: Role
    refresh_token: RefreshToken | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        email: Email,
        password: Password,
        name: Name,
        role: Role,
        refresh_token: RefreshToken | None = None,
    ) -> "Admin":
        admin = cls(
            email=email,
            password=password,
            name=name,
            role=role,
            refresh_token=refresh_token,
            by_factory=True,
        )
        return admin

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email.to_str(),
            "name": self.name.to_str(),
            "role": self.role.to_str(),
            "refresh_token": (
                self.refresh_token.to_str() if self.refresh_token else None
            ),
        }

    def to_model(self):
        return {
            "id": self.id,
            "email": self.email.to_str(),
            "password": self.password.to_str(),
            "name": self.name.to_str(),
            "role": self.role.to_str(),
            "refresh_token": (
                self.refresh_token.to_str() if self.refresh_token else None
            ),
        }
