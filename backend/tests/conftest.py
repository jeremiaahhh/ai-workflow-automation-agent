from __future__ import annotations

import os
from collections.abc import Iterator

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("USE_MOCK_AI", "true")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db, get_engine, get_session_factory, reset_engine_for_tests
from app.main import create_app


@pytest.fixture(autouse=True)
def _isolated_db() -> Iterator[None]:
    get_settings.cache_clear()  # type: ignore[attr-defined]
    reset_engine_for_tests("sqlite:///:memory:")
    Base.metadata.create_all(bind=get_engine())
    yield
    Base.metadata.drop_all(bind=get_engine())


@pytest.fixture
def db_session() -> Iterator[Session]:
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()

    def _override_db() -> Iterator[Session]:
        SessionLocal = get_session_factory()
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
