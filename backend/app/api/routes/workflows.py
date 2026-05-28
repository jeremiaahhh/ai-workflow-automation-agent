from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentPlan
from app.schemas.tool import ToolDefinition
from app.schemas.workflow import (
    ReportResponse,
    WorkflowCreate,
    WorkflowDetail,
    WorkflowStats,
    WorkflowSummary,
)
from app.services.agent_executor_service import AgentExecutorService
from app.services.agent_planner_service import AgentPlannerService
from app.services.report_service import ReportService
from app.services.workflow_service import WorkflowService
from app.tools.registry import default_registry

router = APIRouter(tags=["workflows"])


@router.get("/tools", response_model=list[ToolDefinition])
def list_tools() -> list[ToolDefinition]:
    return default_registry.definitions()


@router.get("/workflows/stats", response_model=WorkflowStats)
def stats(db: Session = Depends(get_db)) -> WorkflowStats:
    return WorkflowService(db).stats()


@router.post(
    "/workflows",
    response_model=WorkflowDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow(
    payload: WorkflowCreate, db: Session = Depends(get_db)
) -> WorkflowDetail:
    service = WorkflowService(db)
    workflow = service.create(payload)
    return service.to_detail(workflow)


@router.get("/workflows", response_model=list[WorkflowSummary])
def list_workflows(db: Session = Depends(get_db)) -> list[WorkflowSummary]:
    service = WorkflowService(db)
    return [service.to_summary(w) for w in service.list_all()]


@router.get("/workflows/{workflow_id}", response_model=WorkflowDetail)
def get_workflow(
    workflow_id: str, db: Session = Depends(get_db)
) -> WorkflowDetail:
    service = WorkflowService(db)
    return service.to_detail(service.get(workflow_id))


@router.post("/workflows/{workflow_id}/plan", response_model=AgentPlan)
def plan_workflow(
    workflow_id: str, db: Session = Depends(get_db)
) -> AgentPlan:
    _, plan = AgentPlannerService(db).plan(workflow_id)
    return plan


@router.post("/workflows/{workflow_id}/approve", response_model=WorkflowDetail)
def approve_workflow(
    workflow_id: str, db: Session = Depends(get_db)
) -> WorkflowDetail:
    service = WorkflowService(db)
    workflow = service.approve(workflow_id)
    return service.to_detail(workflow)


@router.post("/workflows/{workflow_id}/reject", response_model=WorkflowDetail)
def reject_workflow(
    workflow_id: str, db: Session = Depends(get_db)
) -> WorkflowDetail:
    service = WorkflowService(db)
    workflow = service.reject(workflow_id)
    return service.to_detail(workflow)


@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowDetail)
def execute_workflow(
    workflow_id: str, db: Session = Depends(get_db)
) -> WorkflowDetail:
    executor = AgentExecutorService(db)
    workflow = executor.execute(workflow_id)
    return WorkflowService(db).to_detail(workflow)


@router.get("/workflows/{workflow_id}/report", response_model=ReportResponse)
def get_report(
    workflow_id: str, db: Session = Depends(get_db)
) -> ReportResponse:
    return ReportService(db).get_report(workflow_id)
