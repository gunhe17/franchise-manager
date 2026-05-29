from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from franchise_manager.api.config import Cafe24Config
from franchise_manager.api.config import get_cafe24_config


# #
# state

class OAuthStateCache:
    def __init__(self, *, config: Cafe24Config):
        self._config = config
        self._states: dict[str, datetime] = {}

    def issue(self) -> str:
        self._prune()
        state = secrets.token_urlsafe(16)
        self._states[state] = datetime.now(timezone.utc)
        return state

    def consume(self, *, state: str) -> bool:
        self._prune()
        issued_at = self._states.pop(state, None)
        consumed = issued_at is not None
        return consumed

    # #
    # internal

    def _prune(self) -> None:
        # ttl
        ttl = timedelta(seconds=self._config.CAFE24_OAUTH_STATE_TTL_SEC)
        now = datetime.now(timezone.utc)
        expired = [s for s, t in self._states.items() if now - t > ttl]
        for s in expired:
            self._states.pop(s, None)


# #
# token

class OAuthTokenCache:
    def __init__(self, *, config: Cafe24Config):
        self._config = config
        self._access_token: str | None = None
        self._expires_at: datetime | None = None

    def get(self) -> str | None:
        if self._access_token is None or self._expires_at is None:
            return None

        # window
        window = timedelta(seconds=self._config.CAFE24_REFRESH_WINDOW_SEC)
        if datetime.now(self._expires_at.tzinfo) >= self._expires_at - window:
            return None

        return self._access_token

    def set(self, *, access_token: str, expires_at: datetime) -> None:
        self._access_token = access_token
        self._expires_at = expires_at

    def clear(self) -> None:
        self._access_token = None
        self._expires_at = None


# #
# OAuthStateCache

oauth_state_cache = OAuthStateCache(config=get_cafe24_config())


# #
# OAuthTokenCache

oauth_token_cache = OAuthTokenCache(config=get_cafe24_config())
