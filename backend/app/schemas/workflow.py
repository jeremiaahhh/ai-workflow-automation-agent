from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.execution import ExecutionStepStatus
from app.models.workflow import WorkflowStatus


class WorkflowCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    goal: str = Field(min_length=10, max_length=4000)
    context: str | None = Field(default=None, max_length=4000)


class ExecutionStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    position: int
    tool_name: str
    description: str
    arguments: dict[str, Any]
    status: ExecutionStepStatus
    output: dict[str, Any] | None
    error_message: str | None
    duration_ms: int | None
    started_at: datetime | None
    finished_at: datetime | None


class WorkflowSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    goal: str
    status: WorkflowStatus
    used_mock: bool
    created_at: datetime
    updated_at: datetime
    step_count: int = 0
    completed_steps: int = 0


class WorkflowDetail(WorkflowSummary):
    context: str | None
    error_message: str | None
    report_markdown: str | None
    steps: list[ExecutionStepRead] = Field(default_factory=list)


class WorkflowStats(BaseModel):
    total: int
    running: int
    completed: int
    failed: int
    awaiting_approval: int
    avg_step_count: float


class ReportResponse(BaseModel):
    workflow_id: str
    title: str
    status: WorkflowStatus
    markdown: str
    generated_at: datetime
