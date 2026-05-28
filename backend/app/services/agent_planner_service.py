from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import InvalidStateError, NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.execution import ExecutionStep
from app.models.workflow import Workflow, WorkflowStatus
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.agent import AgentPlan
from app.services.llm_service import PlanGenerator, get_plan_generator
from app.tools.registry import ToolRegistry, default_registry

logger = get_logger(__name__)


class AgentPlannerService:
    """Builds a plan for a draft workflow and persists it as `ExecutionStep`s.

    The planner is the only place that talks to the LLM. The output is
    validated against the tool registry — any tool name the planner invents is
    rejected before we touch the database.
    """

    def __init__(
        self,
        db: Session,
        *,
        registry: ToolRegistry | None = None,
        plan_generator: PlanGenerator | None = None,
    ) -> None:
        self.db = db
        self.registry = registry or default_registry
        self.plan_generator = plan_generator or get_plan_generator()
        self.repo = WorkflowRepository(db)
        self.settings = get_settings()

    def plan(self, workflow_id: str) -> tuple[Workflow, AgentPlan]:
        workflow = self.repo.get(workflow_id)
        if workflow is None:
            raise NotFoundError(f"Workflow '{workflow_id}' not found.")
        if workflow.status not in {WorkflowStatus.draft, WorkflowStatus.planned}:
            raise InvalidStateError(
                f"Cannot plan a workflow in status '{workflow.status.value}'.",
                details={"required_status": ["draft", "planned"]},
            )

        plan = self.plan_generator.generate(
            workflow_id=workflow.id,
            goal=workflow.goal,
            context=workflow.context,
            tools=self.registry.definitions(),
            max_steps=self.settings.max_steps_per_plan,
        )

        if not plan.steps:
            raise ValidationError("Planner produced an empty plan.")

        registered = self.registry.names()
        for step in plan.steps:
            if step.tool_name not in registered:
                raise ValidationError(
                    f"Planner referenced unknown tool '{step.tool_name}'.",
                    details={"available_tools": sorted(registered)},
                )

        steps = [
            ExecutionStep(
                position=step.position,
                tool_name=step.tool_name,
                description=step.description,
                arguments=step.arguments,
            )
            for step in plan.steps
        ]
        self.repo.replace_steps(workflow, steps)
        workflow.used_mock = plan.used_mock
        workflow.error_message = None
        workflow = self.repo.set_status(workflow, WorkflowStatus.planned)

        logger.info(
            "workflow_planned",
            workflow_id=workflow.id,
            step_count=len(plan.steps),
            used_mock=plan.used_mock,
        )
        return workflow, plan
