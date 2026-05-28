from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ToolLog(Base):
    """Append-only audit log of tool invocations across all workflows.

    Distinct from `ExecutionStep` (which is the canonical state of a step),
    `ToolLog` is the immutable record used for analytics and debugging.
    """

    __tablename__ = "tool_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    workflow_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    step_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("execution_steps.id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(String(80), nullable=False)
    arguments: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    success: Mapped[bool] = mapped_column(default=True, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
