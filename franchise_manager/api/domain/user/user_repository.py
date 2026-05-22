from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Base
from franchise_manager.api.core.repository import Repository

from franchise_manager.api.domain.user.user import User
from franchise_manager.api.domain.user.phone import Phone
from franchise_manager.api.domain.user.kakao_user_id import KakaoUserId


# #
# model

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    phone: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    password: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    kakao_user_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
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
        CheckConstraint(
            "kakao_user_id IS NOT NULL OR (phone IS NOT NULL AND password IS NOT NULL)",
            name="users_auth_method_check",
        ),
        Index(
            "uq_users_phone_active",
            "phone",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND phone IS NOT NULL"),
        ),
        Index(
            "uq_users_kakao_user_id_active",
            "kakao_user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND kakao_user_id IS NOT NULL"),
        ),
    )


# #
# repository

class UserRepository(Repository[User]):
    # #
    # read

    @abstractmethod
    async def find_by_phone(self, phone: Phone) -> User | None:
        ...

    @abstractmethod
    async def find_by_kakao_user_id(self, kakao_user_id: KakaoUserId) -> User | None:
        ...
