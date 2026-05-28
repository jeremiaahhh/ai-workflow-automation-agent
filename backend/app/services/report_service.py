from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.execution import ExecutionStepStatus
from app.models.workflow import Workflow
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import ReportResponse


class ReportService:
    """Renders the final per-workflow Markdown report.

    The agent may itself invoke `generate_markdown_report_tool` as one of its
    steps — when that happens we prefer the agent's report. Otherwise we
    assemble one from execution outcomes so every workflow has a report
    regardless of whether the planner picked the report tool.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = WorkflowRepository(db)

    def get_report(self, workflow_id: str) -> ReportResponse:
        workflow = self.repo.get(workflow_id)
        if workflow is None:
            raise NotFoundError(f"Workflow '{workflow_id}' not found.")

        markdown = self._extract_agent_report(workflow) or self._compose_report(workflow)
        workflow.report_markdown = markdown
        self.repo.save(workflow)

        return ReportResponse(
            workflow_id=workflow.id,
            title=workflow.title,
            status=workflow.status,
            markdown=markdown,
            generated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _extract_agent_report(workflow: Workflow) -> str | None:
        for step in workflow.steps:
            if (
                step.tool_name == "generate_markdown_report_tool"
                and step.status == ExecutionStepStatus.succeeded
                and isinstance(step.output, dict)
                and step.output.get("markdown")
            ):
                return str(step.output["markdown"])
        return None

    @staticmethod
    def _compose_report(workflow: Workflow) -> str:
        lines: list[str] = [
            f"# {workflow.title}",
            "",
            f"**Status:** {workflow.status.value}  ",
            f"**Mode:** {'mock' if workflow.used_mock else 'live'}  ",
            f"**Created:** {workflow.created_at.isoformat()}",
            "",
            "## Goal",
            "",
            workflow.goal.strip(),
        ]
        if workflow.context:
            lines += ["", "## Context", "", workflow.context.strip()]

        lines += ["", "## Execution Timeline", ""]
        for step in workflow.steps:
            status = step.status.value
            duration = f"{step.duration_ms} ms" if step.duration_ms else "—"
            lines.append(
                f"### Step {step.position}: `{step.tool_name}` "
                f"_(status: {status}, duration: {duration})_"
            )
            lines.append("")
            lines.append(step.description.strip())
            lines.append("")
            if step.error_message:
                lines.append(f"> Error: {step.error_message}")
                lines.append("")
                continue
            if isinstance(step.output, dict):
                preview = ReportService._render_output_preview(
                    step.tool_name, step.output
                )
                if preview:
                    lines.append(preview)
                    lines.append("")

        if workflow.error_message:
            lines += ["## Error", "", workflow.error_message, ""]

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def _render_output_preview(tool_name: str, output: dict) -> str:
        if tool_name == "mock_web_search_tool":
            results = output.get("results", [])
            if not results:
                return "_no results_"
            rendered = [f"- [{r['title']}]({r['url']}) — {r['snippet']}" for r in results]
            return "\n".join(rendered)
        if tool_name in {"summarize_text_tool"}:
            return f"> {output.get('summary', '').strip()}"
        if tool_name == "extract_key_points_tool":
            points = output.get("points", [])
            return "\n".join(f"- {p['text']}" for p in points)
        if tool_name == "create_todo_list_tool":
            items = output.get("items", [])
            return "\n".join(
                f"{item['position']}. **{item['title']}** — {item['detail']}"
                for item in items
            )
        if tool_name == "generate_markdown_report_tool":
            return output.get("markdown", "")
        return ""
