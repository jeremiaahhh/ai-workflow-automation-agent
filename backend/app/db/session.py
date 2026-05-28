from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _build_engine(database_url: str) -> Engine:
    connect_args: dict = {}
    kwargs: dict = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if ":memory:" in database_url:
            kwargs["poolclass"] = StaticPool
    return create_engine(database_url, connect_args=connect_args, **kwargs)


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = _build_engine(get_settings().database_url)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False
        )
    return _SessionLocal


def get_db() -> Iterator[Session]:
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_engine_for_tests(database_url: str) -> None:
    """Tests rebind the engine to an in-memory SQLite."""
    global _engine, _SessionLocal
    _engine = _build_engine(database_url)
    _SessionLocal = sessionmaker(
        bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
