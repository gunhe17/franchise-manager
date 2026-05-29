from __future__ import annotations

import traceback
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from franchise_manager.api.config import Env, get_app_config
from franchise_manager.api.core.exception import AppError, ClientError, DevelopError


class ExceptionHandler:
    def __init__(
        self,
        *,
        exception_class: type[Exception],
        handler: Callable[[Request, Exception], Any],
    ):
        self._exception_class = exception_class
        self._handler = handler

    def register(self, app: FastAPI):
        app.add_exception_handler(self._exception_class, self._handler)


# #
# factory

def client() -> ExceptionHandler:
    async def handler(_: Request, exc: Exception) -> JSONResponse:
        # env
        env = get_app_config().APPLICATION_ENVIRONMENT
        is_dev_phase = env == Env.DEVELOP or env == Env.TEST

        # body
        body = {
            "error": type(exc).__name__,
            "message": getattr(exc, "msg", str(exc)),
        }
        if is_dev_phase and isinstance(exc, AppError):
            body["traceback"] = exc.__trace_back__()

        return JSONResponse(body, status_code=getattr(exc, "code", 400))

    return ExceptionHandler(
        exception_class=ClientError,
        handler=handler,
    )


def develop() -> ExceptionHandler:
    async def handler(_: Request, exc: Exception) -> JSONResponse:
        # log
        traceback.print_exception(type(exc), exc, exc.__traceback__)

        # env
        env = get_app_config().APPLICATION_ENVIRONMENT
        is_dev_phase = env == Env.DEVELOP or env == Env.TEST

        # body
        if is_dev_phase and isinstance(exc, AppError):
            body = {
                "error": type(exc).__name__,
                "message": getattr(exc, "msg", str(exc)),
                "traceback": exc.__trace_back__(),
            }
        else:
            body = {
                "error": "InternalServerError",
                "message": "internal server error",
            }

        return JSONResponse(body, status_code=500)

    return ExceptionHandler(
        exception_class=DevelopError,
        handler=handler,
    )
