from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


class ToolResult(BaseModel):
    success: bool
    output: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: int = Field(default=0, ge=0)
