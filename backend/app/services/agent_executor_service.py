from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import InvalidStateError, NotFoundError
from app.core.logging import get_logger
from app.core.security import (
    assert_executable_state,
    assert_tool_allowed,
    sanitize_tool_args,
)
from app.models.execution import ExecutionStep, ExecutionStepStatus
from app.models.workflow import Workflow, WorkflowStatus
from app.repositories.execution_repository import ExecutionRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.tools.registry import ToolRegistry, default_registry

logger = get_logger(__name__)


class AgentExecutorService:
    """Walks an approved plan one step at a time and writes outcomes back.

    The executor is intentionally simple: each step gets its own
    `assert_tool_allowed` + arg sanitation gate, then is dispatched through the
    `Tool.invoke` wrapper which already times and packages the result. The
    workflow transitions are explicit so the UI's status badge is never lying
    about the underlying state.
    """

    def __init__(
        self,
        db: Session,
        *,
        registry: ToolRegistry | None = None,
    ) -> None:
        self.db = db
        self.registry = registry or default_registry
        self.workflow_repo = WorkflowRepository(db)
        self.exec_repo = ExecutionRepository(db)

    def execute(self, workflow_id: str) -> Workflow:
        workflow = self.workflow_repo.get(workflow_id)
        if workflow is None:
            raise NotFoundError(f"Workflow '{workflow_id}' not found.")
        if workflow.status != WorkflowStatus.approved:
            raise InvalidStateError(
                f"Workflow must be approved before execution (current: '{workflow.status.value}').",
                details={"required_status": ["approved"]},
            )
        if not workflow.steps:
            raise InvalidStateError("Workflow has no steps to execute.")

        assert_executable_state(workflow.status.value)
        registered = self.registry.names()
        for step in workflow.steps:
            assert_tool_allowed(step.tool_name, registered)

        workflow = self.workflow_repo.set_status(workflow, WorkflowStatus.running)
        any_failed = False

        for step in workflow.steps:
            self._run_step(workflow, step)
            self.db.refresh(step)
            if step.status == ExecutionStepStatus.failed:
                any_failed = True
                break

        if any_failed:
            workflow.error_message = "One or more steps failed."
            workflow = self.workflow_repo.set_status(workflow, WorkflowStatus.failed)
        else:
            workflow = self.workflow_repo.set_status(workflow, WorkflowStatus.completed)

        logger.info(
            "workflow_executed",
            workflow_id=workflow.id,
            final_status=workflow.status.value,
            step_count=len(workflow.steps),
        )
        return workflow

    def _run_step(self, workflow: Workflow, step: ExecutionStep) -> None:
        started_at = datetime.now(timezone.utc)
        self.workflow_repo.mark_step(
            step,
            status=ExecutionStepStatus.running,
            started_at=started_at,
        )

        try:
            sanitized = sanitize_tool_args(step.arguments)
            tool = self.registry.get(step.tool_name)
            result = tool.invoke(sanitized)
        except Exception as exc:  # noqa: BLE001
            finished_at = datetime.now(timezone.utc)
            self.workflow_repo.mark_step(
                step,
                status=ExecutionStepStatus.failed,
                error=str(exc),
                finished_at=finished_at,
                duration_ms=int((finished_at - started_at).total_seconds() * 1000),
            )
            self.exec_repo.record(
                workflow_id=workflow.id,
                step_id=step.id,
                tool_name=step.tool_name,
                arguments=step.arguments,
                output=None,
                success=False,
                error_message=str(exc),
                duration_ms=step.duration_ms or 0,
            )
            logger.error(
                "step_failed",
                workflow_id=workflow.id,
                step_id=step.id,
                tool=step.tool_name,
                error=str(exc),
            )
            return

        finished_at = datetime.now(timezone.utc)
        self.workflow_repo.mark_step(
            step,
            status=(
                ExecutionStepStatus.succeeded
                if result.success
                else ExecutionStepStatus.failed
            ),
            output=result.output,
            error=result.error,
            duration_ms=result.duration_ms,
            finished_at=finished_at,
        )
        self.exec_repo.record(
            workflow_id=workflow.id,
            step_id=step.id,
            tool_name=step.tool_name,
            arguments=step.arguments,
            output=result.output,
            success=result.success,
            error_message=result.error,
            duration_ms=result.duration_ms,
        )
        logger.info(
            "step_completed",
            workflow_id=workflow.id,
            step_id=step.id,
            tool=step.tool_name,
            success=result.success,
            duration_ms=result.duration_ms,
        )
