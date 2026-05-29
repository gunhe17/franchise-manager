from __future__ import annotations

from franchise_manager.api.core.exception import ClientError


# #
# base

class DomainError(ClientError):
    ...


# #
# validation — value object

class InvalidError(DomainError):
    def __init__(self, target: str = "값"):
        super().__init__(
            message=f"{target}: 타입이 유효하지 않습니다.",
            code=400,
        )


class InvalidFormatError(DomainError):
    def __init__(self, target: str = "값"):
        super().__init__(
            message=f"{target}: 형식이 유효하지 않습니다.",
            code=400,
        )


# #
# validation — entity

class InvalidAuthCredentialError(DomainError):
    def __init__(self):
        super().__init__(
            message="인증 수단이 올바르지 않습니다. (카카오 ID 또는 휴대폰+비밀번호 필수)",
            code=400,
        )


# #
# lookup

class NotFoundError(DomainError):
    def __init__(self, target: str, identifier: str):
        super().__init__(
            message=f"\n\t {target}, 찾을 수 없습니다. (식별자: {identifier})",
            code=404,
        )


# #
# uniqueness

class AlreadyExistsError(DomainError):
    def __init__(self, target: str, identifier: str):
        super().__init__(
            message=f"\n\t {target}, 이미 존재합니다. (식별자: {identifier})",
            code=409,
        )
