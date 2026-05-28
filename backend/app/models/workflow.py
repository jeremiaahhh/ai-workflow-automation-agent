from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WorkflowStatus(str, enum.Enum):
    draft = "draft"
    planned = "planned"
    approved = "approved"
    running = "running"
    completed = "completed"
    failed = "failed"
    rejected = "rejected"


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus, native_enum=False, length=20),
        nullable=False,
        default=WorkflowStatus.draft,
    )

    report_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    used_mock: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )

    steps: Mapped[list["ExecutionStep"]] = relationship(  # noqa: F821
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="ExecutionStep.position",
    )
