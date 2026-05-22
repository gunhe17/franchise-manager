from __future__ import annotations

import base64
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from franchise_manager.api.config import Cafe24Config
from franchise_manager.api.config import get_cafe24_config


# #
# cafe24

class Cafe24:
    def __init__(self, *, config: Cafe24Config):
        self._config = config
        self._access_token: str | None = None
        self._expires_at: datetime | None = None

    async def start_oauth(self, *, session: AsyncSession) -> str:
        state = await self._issue_state(session=session)
        url = self._authorize_url(state=state)
        return url

    async def complete_oauth(
        self,
        *,
        session: AsyncSession,
        code: str,
        state: str,
    ) -> None:
        if not await self._consume_state(session=session, state=state):
            raise  # InvalidStateError

        token = await self._exchange_code(code=code)
        await self._save_token(session=session, token=token)

    async def get_access_token(self, *, session: AsyncSession) -> str:
        if self._access_token is not None and self._expires_at is not None:
            if datetime.now(self._expires_at.tzinfo) < self._expires_at - timedelta(seconds=self._config.CAFE24_REFRESH_WINDOW_SEC):
                return self._access_token

        refresh_token = await self._get_setting(session=session, key=self._config.CAFE24_REFRESH_KEY)
        if refresh_token is None:
            raise  # NotConnectedError

        new_token = await self._refresh(refresh_token=refresh_token)
        await self._save_token(session=session, token=new_token)

        access_token = new_token["access_token"]
        return access_token

    # #
    # state

    async def _issue_state(self, *, session: AsyncSession) -> str:
        state = secrets.token_urlsafe(16)
        await session.execute(
            text("INSERT INTO cafe24_oauth_states (state, created_at) VALUES (:state, NOW())"),
            {"state": state},
        )
        return state

    async def _consume_state(self, *, session: AsyncSession, state: str) -> bool:
        result = await session.execute(
            text("DELETE FROM cafe24_oauth_states WHERE state = :state RETURNING state"),
            {"state": state},
        )
        consumed = result.first() is not None
        return consumed

    # #
    # http

    def _authorize_url(self, *, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self._config.CAFE24_CLIENT_ID,
            "redirect_uri": self._config.CAFE24_REDIRECT_URI,
            "scope": self._config.CAFE24_SCOPE,
            "state": state,
        }
        url = f"https://{self._config.CAFE24_MALL_ID}.cafe24api.com/api/v2/oauth/authorize?{urlencode(params)}"
        return url

    async def _exchange_code(self, *, code: str) -> dict:
        async with httpx.AsyncClient(timeout=self._config.CAFE24_TIMEOUT_SEC) as http:
            response = await http.post(
                url=f"https://{self._config.CAFE24_MALL_ID}.cafe24api.com/api/v2/oauth/token",
                headers={
                    "Authorization": f"Basic {self._basic_auth()}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self._config.CAFE24_REDIRECT_URI,
                },
            )
            response.raise_for_status()

        token = response.json()
        return token

    async def _refresh(self, *, refresh_token: str) -> dict:
        async with httpx.AsyncClient(timeout=self._config.CAFE24_TIMEOUT_SEC) as http:
            response = await http.post(
                url=f"https://{self._config.CAFE24_MALL_ID}.cafe24api.com/api/v2/oauth/token",
                headers={
                    "Authorization": f"Basic {self._basic_auth()}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )
            response.raise_for_status()

        token = response.json()
        return token

    def _basic_auth(self) -> str:
        return base64.b64encode(
            f"{self._config.CAFE24_CLIENT_ID}:{self._config.CAFE24_CLIENT_SECRET}".encode()
        ).decode()

    # #
    # token

    async def _save_token(self, *, session: AsyncSession, token: dict) -> None:
        await self._upsert_setting(
            session=session,
            key=self._config.CAFE24_REFRESH_KEY,
            value=token["refresh_token"],
        )
        await self._upsert_setting(
            session=session,
            key=self._config.CAFE24_REFRESH_EXPIRES_KEY,
            value=token["refresh_token_expires_at"],
        )
        self._access_token = token["access_token"]
        self._expires_at = datetime.fromisoformat(token["expires_at"])

    # #
    # settings

    async def _get_setting(self, *, session: AsyncSession, key: str) -> str | None:
        result = await session.execute(
            text("SELECT value FROM settings WHERE key = :key"),
            {"key": key},
        )
        row = result.first()
        return row[0] if row else None

    async def _upsert_setting(self, *, session: AsyncSession, key: str, value: str) -> None:
        await session.execute(
            text(
                "INSERT INTO settings (key, value, updated_at) "
                "VALUES (:key, :value, NOW()) "
                "ON CONFLICT (key) DO UPDATE "
                "SET value = EXCLUDED.value, updated_at = NOW()"
            ),
            {"key": key, "value": value},
        )


_cafe24 = Cafe24(config=get_cafe24_config())


# #
# Cafe24

def cafe24() -> Cafe24:
    return _cafe24
