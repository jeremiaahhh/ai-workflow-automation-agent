from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, workflows
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.base import Base
from app.db.session import get_engine
from app.models import ExecutionStep, ToolLog, Workflow  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger = get_logger(__name__)
    settings = get_settings()
    Base.metadata.create_all(bind=get_engine())
    logger.info(
        "service_started",
        app=settings.app_name,
        mock_mode=settings.is_mock_mode,
        provider=settings.ai_provider,
    )
    yield
    logger.info("service_stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        description=(
            "Plan-approve-execute AI agent with a registered tool catalog, "
            "structured execution timeline, and Markdown report output."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(workflows.router)
    return app


app = create_app()
