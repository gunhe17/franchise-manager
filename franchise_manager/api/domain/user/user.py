from __future__ import annotations

from dataclasses import dataclass

from franchise_manager.api.core.entity import Entity
from franchise_manager.api.core.validate import typecheck

from franchise_manager.api.domain.user.name import Name
from franchise_manager.api.domain.user.phone import Phone
from franchise_manager.api.domain.user.password import Password
from franchise_manager.api.domain.user.kakao_user_id import KakaoUserId
from franchise_manager.api.domain.user.refresh_token import RefreshToken


@dataclass(frozen=True, kw_only=True)
class User(Entity):
    name: Name
    phone: Phone | None = None
    password: Password | None = None
    kakao_user_id: KakaoUserId | None = None
    refresh_token: RefreshToken | None = None

    # #
    # factory

    @classmethod
    @typecheck
    def new(
        cls,
        *,
        name: Name,
        phone: Phone | None = None,
        password: Password | None = None,
        kakao_user_id: KakaoUserId | None = None,
        refresh_token: RefreshToken | None = None,
    ) -> "User":
        # auth
        if kakao_user_id is None and (phone is None or password is None):
            raise  # InvalidAuthCredentialError

        user = cls(
            name=name,
            phone=phone,
            password=password,
            kakao_user_id=kakao_user_id,
            refresh_token=refresh_token,
            by_factory=True,
        )
        return user

    # #
    # query

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name.to_str(),
            "phone": self.phone.to_str() if self.phone else None,
            "password": self.password.to_str() if self.password else None,
            "kakao_user_id": self.kakao_user_id.to_str() if self.kakao_user_id else None,
            "refresh_token": self.refresh_token.to_str() if self.refresh_token else None,
        }

    def to_model(self):
        return {
            "id": self.id,
            "name": self.name.to_str(),
            "phone": self.phone.to_str() if self.phone else None,
            "password": self.password.to_str() if self.password else None,
            "kakao_user_id": self.kakao_user_id.to_str() if self.kakao_user_id else None,
            "refresh_token": self.refresh_token.to_str() if self.refresh_token else None,
        }
