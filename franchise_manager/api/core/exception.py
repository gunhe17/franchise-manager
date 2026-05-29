from __future__ import annotations

import traceback


# #
# base

class AppError(Exception):
    def __init__(self, message: str | None = None, code: int | None = None):
        self.msg = message
        self.code = code
    
    def __trace_back__(self) -> str:
        return ''.join(traceback.format_exception(type(self), self, self.__traceback__))


# #
# categories

class ClientError(AppError):
    ...


class DevelopError(AppError):
    ...