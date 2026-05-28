from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base application error. Subclass for typed failures."""

    status_code: int = 400
    error_code: str = "app_error"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class InvalidStateError(AppError):
    status_code = 409
    error_code = "invalid_state"


class ToolNotFoundError(AppError):
    status_code = 400
    error_code = "tool_not_found"


class ToolExecutionError(AppError):
    status_code = 500
    error_code = "tool_execution_failed"


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_failed"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "app_error",
            path=request.url.path,
            code=exc.error_code,
            message=exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_failed",
                    "message": "Request validation failed.",
                    "details": {"errors": exc.errors()},
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.error("database_error", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "database_error",
                    "message": "An internal database error occurred.",
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_error", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                }
            },
        )
