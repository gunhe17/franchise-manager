from __future__ import annotations

import base64
from urllib.parse import urlencode

import httpx

from franchise_manager.api.config import Cafe24Config
from franchise_manager.api.config import get_cafe24_config


# #
# cafe24

class Cafe24:
    def __init__(self, *, config: Cafe24Config):
        self._config = config

    # #
    # query

    def get_authorize_url(self, *, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self._config.CAFE24_CLIENT_ID,
            "redirect_uri": self._config.CAFE24_REDIRECT_URI,
            "scope": self._config.CAFE24_SCOPE,
            "state": state,
        }
        url = f"https://{self._config.CAFE24_MALL_ID}.cafe24api.com/api/v2/oauth/authorize?{urlencode(params)}"
        return url

    # #
    # command

    async def exchange_code(self, *, code: str) -> dict:
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

    async def refresh_token(self, *, refresh_token: str) -> dict:
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

    # #
    # internal

    def _basic_auth(self) -> str:
        return base64.b64encode(
            f"{self._config.CAFE24_CLIENT_ID}:{self._config.CAFE24_CLIENT_SECRET}".encode()
        ).decode()


# #
# Cafe24

cafe24 = Cafe24(config=get_cafe24_config())