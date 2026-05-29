from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, String, Uuid, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from franchise_manager.api.core.model import Model

from franchise_manager.api.domain.user.user import User
from franchise_manager.api.domain.user.name import Name
from franchise_manager.api.domain.user.phone import Phone
from franchise_manager.api.domain.user.password import Password
from franchise_manager.api.domain.user.kakao_user_id import KakaoUserId
from franchise_manager.api.domain.user.refresh_token import RefreshToken

from franchise_manager.api.infrastructure.postgresql.repository import PostgresRepository


# #
# model

class UserModel(Model):
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
# mapper

def _to_user(model: UserModel) -> User:
    user = User(
        id=model.id,
        name=Name.from_str(model.name),
        phone=Phone.from_str(model.phone) if model.phone else None,
        password=Password.from_str(model.password) if model.password else None,
        kakao_user_id=KakaoUserId.from_str(model.kakao_user_id) if model.kakao_user_id else None,
        refresh_token=RefreshToken.from_str(model.refresh_token) if model.refresh_token else None,
        by_factory=True,
    )
    return user


# #
# repository

class UserRepository(PostgresRepository[User, UserModel]):
    model = UserModel
    mapper = _to_user

    # #
    # read

    async def find_by_phone(self, *, session: AsyncSession, phone: Phone) -> User | None:
        user = await self._find_by(session=session, column="phone", value=phone.to_str())
        return user

    async def find_by_kakao_user_id(self, *, session: AsyncSession, kakao_user_id: KakaoUserId) -> User | None:
        user = await self._find_by(session=session, column="kakao_user_id", value=kakao_user_id.to_str())
        return user


# #
# UserRepository

user_repository = UserRepository()  # type: ignore[call-arg]
