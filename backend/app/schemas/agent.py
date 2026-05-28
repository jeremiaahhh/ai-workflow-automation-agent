from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlannedStep(BaseModel):
    position: int = Field(ge=1)
    tool_name: str
    description: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentPlan(BaseModel):
    workflow_id: str
    rationale: str
    steps: list[PlannedStep]
    used_mock: bool = True


class StepUpdate(BaseModel):
    """Live update emitted while the executor walks the plan (not streamed yet,
    but the shape is stable enough to add SSE later)."""

    step_id: str
    position: int
    tool_name: str
    status: str
    output: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: int = 0
