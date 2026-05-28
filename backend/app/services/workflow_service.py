from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import InvalidStateError, NotFoundError
from app.core.logging import get_logger
from app.models.execution import ExecutionStepStatus
from app.models.workflow import Workflow, WorkflowStatus
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import (
    ExecutionStepRead,
    WorkflowCreate,
    WorkflowDetail,
    WorkflowStats,
    WorkflowSummary,
)

logger = get_logger(__name__)


class WorkflowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = WorkflowRepository(db)

    def create(self, payload: WorkflowCreate) -> Workflow:
        workflow = self.repo.create(
            title=payload.title,
            goal=payload.goal,
            context=payload.context,
            used_mock=get_settings().is_mock_mode,
        )
        logger.info("workflow_created", workflow_id=workflow.id, title=workflow.title)
        return workflow

    def get(self, workflow_id: str) -> Workflow:
        workflow = self.repo.get(workflow_id)
        if workflow is None:
            raise NotFoundError(f"Workflow '{workflow_id}' not found.")
        return workflow

    def list_all(self) -> list[Workflow]:
        return self.repo.list_all()

    def approve(self, workflow_id: str) -> Workflow:
        workflow = self.get(workflow_id)
        if workflow.status != WorkflowStatus.planned:
            raise InvalidStateError(
                f"Cannot approve a workflow in status '{workflow.status.value}'.",
                details={"required_status": ["planned"]},
            )
        return self.repo.set_status(workflow, WorkflowStatus.approved)

    def reject(self, workflow_id: str) -> Workflow:
        workflow = self.get(workflow_id)
        if workflow.status != WorkflowStatus.planned:
            raise InvalidStateError(
                f"Cannot reject a workflow in status '{workflow.status.value}'.",
                details={"required_status": ["planned"]},
            )
        return self.repo.set_status(workflow, WorkflowStatus.rejected)

    def stats(self) -> WorkflowStats:
        return WorkflowStats(**self.repo.stats())

    @staticmethod
    def to_summary(workflow: Workflow) -> WorkflowSummary:
        completed = sum(
            1
            for s in workflow.steps
            if s.status == ExecutionStepStatus.succeeded
        )
        return WorkflowSummary(
            id=workflow.id,
            title=workflow.title,
            goal=workflow.goal,
            status=workflow.status,
            used_mock=workflow.used_mock,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            step_count=len(workflow.steps),
            completed_steps=completed,
        )

    @classmethod
    def to_detail(cls, workflow: Workflow) -> WorkflowDetail:
        summary = cls.to_summary(workflow)
        return WorkflowDetail(
            **summary.model_dump(),
            context=workflow.context,
            error_message=workflow.error_message,
            report_markdown=workflow.report_markdown,
            steps=[ExecutionStepRead.model_validate(s) for s in workflow.steps],
        )
