from __future__ import annotations

import os
from abc import ABC, abstractmethod


# #
# postgres

class PostgresConfig(ABC):
    @property
    @abstractmethod
    def POSTGRES_HOST(self) -> str: ...

    @property
    @abstractmethod
    def POSTGRES_PORT(self) -> int: ...

    @property
    @abstractmethod
    def POSTGRES_USER(self) -> str: ...

    @property
    @abstractmethod
    def POSTGRES_PASSWORD(self) -> str: ...

    @property
    @abstractmethod
    def POSTGRES_DB(self) -> str: ...

    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )


class DevelopPostgresConfig(PostgresConfig):
    @property
    def POSTGRES_HOST(self) -> str:
        return os.environ["DEVELOP_POSTGRES_HOST"]

    @property
    def POSTGRES_PORT(self) -> int:
        return int(os.environ["DEVELOP_POSTGRES_CONTAINER_PORT"])

    @property
    def POSTGRES_USER(self) -> str:
        return os.environ["DEVELOP_POSTGRES_USER"]

    @property
    def POSTGRES_PASSWORD(self) -> str:
        return os.environ["DEVELOP_POSTGRES_PASSWORD"]

    @property
    def POSTGRES_DB(self) -> str:
        return os.environ["DEVELOP_POSTGRES_DB"]


def get_postgres_config() -> PostgresConfig:
    config = DevelopPostgresConfig()
    return config


# #
# test postgres

class TestPostgresConfig(PostgresConfig):
    @property
    def POSTGRES_HOST(self) -> str:
        return os.environ["TEST_POSTGRES_HOST"]

    @property
    def POSTGRES_PORT(self) -> int:
        return int(os.environ["TEST_POSTGRES_CONTAINER_PORT"])

    @property
    def POSTGRES_USER(self) -> str:
        return os.environ["TEST_POSTGRES_USER"]

    @property
    def POSTGRES_PASSWORD(self) -> str:
        return os.environ["TEST_POSTGRES_PASSWORD"]

    @property
    def POSTGRES_DB(self) -> str:
        return os.environ["TEST_POSTGRES_DB"]


def get_test_postgres_config() -> PostgresConfig:
    config = TestPostgresConfig()
    return config


# #
# cafe24

class Cafe24Config(ABC):
    @property
    @abstractmethod
    def CAFE24_MALL_ID(self) -> str: ...

    @property
    @abstractmethod
    def CAFE24_CLIENT_ID(self) -> str: ...

    @property
    @abstractmethod
    def CAFE24_CLIENT_SECRET(self) -> str: ...

    @property
    @abstractmethod
    def CAFE24_REDIRECT_URI(self) -> str: ...

    @property
    @abstractmethod
    def CAFE24_SCOPE(self) -> str: ...

    @property
    @abstractmethod
    def CAFE24_API_VERSION(self) -> str: ...

    @property
    @abstractmethod
    def CAFE24_TIMEOUT_SEC(self) -> int: ...

    @property
    @abstractmethod
    def CAFE24_REFRESH_WINDOW_SEC(self) -> int: ...

    @property
    @abstractmethod
    def CAFE24_REFRESH_KEY(self) -> str: ...

    @property
    @abstractmethod
    def CAFE24_REFRESH_EXPIRES_KEY(self) -> str: ...


class DevelopCafe24Config(Cafe24Config):
    @property
    def CAFE24_MALL_ID(self) -> str:
        return os.environ["DEVELOP_CAFE24_MALL_ID"]

    @property
    def CAFE24_CLIENT_ID(self) -> str:
        return os.environ["DEVELOP_CAFE24_CLIENT_ID"]

    @property
    def CAFE24_CLIENT_SECRET(self) -> str:
        return os.environ["DEVELOP_CAFE24_CLIENT_SECRET"]

    @property
    def CAFE24_REDIRECT_URI(self) -> str:
        return os.environ["DEVELOP_CAFE24_REDIRECT_URI"]

    @property
    def CAFE24_SCOPE(self) -> str:
        return "mall.read_order"

    @property
    def CAFE24_API_VERSION(self) -> str:
        return os.environ["DEVELOP_CAFE24_API_VERSION"]

    @property
    def CAFE24_TIMEOUT_SEC(self) -> int:
        return 10

    @property
    def CAFE24_REFRESH_WINDOW_SEC(self) -> int:
        return 300

    @property
    def CAFE24_REFRESH_KEY(self) -> str:
        return "cafe24_refresh_token"

    @property
    def CAFE24_REFRESH_EXPIRES_KEY(self) -> str:
        return "cafe24_refresh_token_expires_at"


def get_cafe24_config() -> Cafe24Config:
    config = DevelopCafe24Config()
    return config
