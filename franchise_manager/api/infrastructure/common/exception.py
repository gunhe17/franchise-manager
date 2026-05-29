from __future__ import annotations

from franchise_manager.api.core.exception import DevelopError


# #
# base

class InfrastructureError(DevelopError):
    ...


# #
# specific

class ExternalApiError(InfrastructureError):
    def __init__(self, api: str, reason: str):
        super().__init__(
            message=f"\n\t 외부 API 호출 실패 ({api}): {reason}",
            code=500,
        )


class DatabaseError(InfrastructureError):
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"\n\t 데이터베이스 오류 ({operation}): {reason}",
            code=500,
        )
