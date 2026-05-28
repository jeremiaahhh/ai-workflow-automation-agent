from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.execution import ExecutionStep, ExecutionStepStatus
from app.models.workflow import Workflow, WorkflowStatus


class WorkflowRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self, *, title: str, goal: str, context: str | None, used_mock: bool
    ) -> Workflow:
        workflow = Workflow(
            title=title.strip(),
            goal=goal.strip(),
            context=context.strip() if context else None,
            used_mock=used_mock,
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def get(self, workflow_id: str) -> Workflow | None:
        stmt = (
            select(Workflow)
            .where(Workflow.id == workflow_id)
            .options(selectinload(Workflow.steps))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[Workflow]:
        stmt = (
            select(Workflow)
            .options(selectinload(Workflow.steps))
            .order_by(Workflow.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def save(self, workflow: Workflow) -> Workflow:
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def set_status(self, workflow: Workflow, status: WorkflowStatus) -> Workflow:
        workflow.status = status
        return self.save(workflow)

    def stats(self) -> dict[str, float]:
        total = self.db.execute(select(func.count(Workflow.id))).scalar() or 0
        by_status = dict(
            self.db.execute(
                select(Workflow.status, func.count(Workflow.id)).group_by(
                    Workflow.status
                )
            ).all()
        )
        avg_steps = (
            self.db.execute(
                select(func.count(ExecutionStep.id) * 1.0 / func.count(func.distinct(Workflow.id)))
                .select_from(Workflow)
                .join(ExecutionStep, ExecutionStep.workflow_id == Workflow.id, isouter=True)
            ).scalar()
            or 0
        )
        return {
            "total": total,
            "running": int(by_status.get(WorkflowStatus.running, 0)),
            "completed": int(by_status.get(WorkflowStatus.completed, 0)),
            "failed": int(by_status.get(WorkflowStatus.failed, 0)),
            "awaiting_approval": int(by_status.get(WorkflowStatus.planned, 0)),
            "avg_step_count": float(round(avg_steps, 2)),
        }

    def replace_steps(self, workflow: Workflow, steps: list[ExecutionStep]) -> None:
        workflow.steps.clear()
        self.db.flush()
        for step in steps:
            workflow.steps.append(step)
        self.db.commit()
        self.db.refresh(workflow)

    def mark_step(
        self,
        step: ExecutionStep,
        *,
        status: ExecutionStepStatus,
        output: dict | None = None,
        error: str | None = None,
        duration_ms: int | None = None,
        started_at=None,
        finished_at=None,
    ) -> ExecutionStep:
        step.status = status
        if output is not None:
            step.output = output
        if error is not None:
            step.error_message = error
        if duration_ms is not None:
            step.duration_ms = duration_ms
        if started_at is not None:
            step.started_at = started_at
        if finished_at is not None:
            step.finished_at = finished_at
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step
