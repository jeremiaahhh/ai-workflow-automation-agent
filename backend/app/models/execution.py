from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExecutionStepStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    skipped = "skipped"


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    workflow_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    tool_name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    arguments: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    status: Mapped[ExecutionStepStatus] = mapped_column(
        Enum(ExecutionStepStatus, native_enum=False, length=20),
        nullable=False,
        default=ExecutionStepStatus.pending,
    )

    output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)

    workflow: Mapped["Workflow"] = relationship(back_populates="steps")  # noqa: F821
