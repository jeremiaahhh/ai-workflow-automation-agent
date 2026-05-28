from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.tools.registry import default_registry

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "mock_mode": settings.is_mock_mode,
        "registered_tools": sorted(default_registry.names()),
    }
