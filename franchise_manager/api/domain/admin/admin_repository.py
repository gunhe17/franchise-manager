from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, String, Uuid, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.admin.admin import Admin
from franchise_manager.api.domain.admin.email import Email
from franchise_manager.api.domain.admin.name import Name
from franchise_manager.api.domain.admin.password import Password
from franchise_manager.api.domain.admin.role import Role
from franchise_manager.api.domain.admin.refresh_token import RefreshToken

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class AdminModel(Model):
    __tablename__ = "admins"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    refresh_token: Mapped[str | None] = mapped_column(
        String,
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

    __table_args__ = (
        Index(
            "uq_admins_email_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


# #
# mapper

def _to_admin(model: AdminModel) -> Admin:
    admin = Admin(
        id=model.id,
        email=Email.from_str(model.email),
        password=Password.from_str(model.password),
        name=Name.from_str(model.name),
        role=Role.from_str(model.role),
        refresh_token=RefreshToken.from_str(model.refresh_token) if model.refresh_token else None,
        by_factory=True,
    )
    return admin


# #
# repository

class AdminRepository(PostgresRepository[Admin, AdminModel]):
    model = AdminModel
    mapper = _to_admin

    # #
    # read

    async def find_by_email(self, *, session: AsyncSession, email: Email) -> Admin | None:
        admin = await self._find_by(session=session, column="email", value=email.to_str())
        return admin


# #
# AdminRepository

admin_repository = AdminRepository()  # type: ignore[call-arg]
