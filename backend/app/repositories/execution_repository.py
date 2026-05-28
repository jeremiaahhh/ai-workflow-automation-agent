from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.tool_log import ToolLog


class ExecutionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        workflow_id: str,
        step_id: str,
        tool_name: str,
        arguments: dict,
        output: dict | None,
        success: bool,
        error_message: str | None,
        duration_ms: int,
    ) -> ToolLog:
        log = ToolLog(
            workflow_id=workflow_id,
            step_id=step_id,
            tool_name=tool_name,
            arguments=arguments,
            output=output,
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
