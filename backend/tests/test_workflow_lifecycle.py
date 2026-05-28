from __future__ import annotations

from fastapi.testclient import TestClient


def _create_workflow(client: TestClient) -> dict:
    response = client.post(
        "/workflows",
        json={
            "title": "Research agent observability",
            "goal": "Compile a short briefing on best practices for AI agent observability.",
            "context": "Internal write-up for the platform team.",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_full_plan_approve_execute_flow(client: TestClient) -> None:
    workflow = _create_workflow(client)
    workflow_id = workflow["id"]
    assert workflow["status"] == "draft"
    assert workflow["used_mock"] is True

    plan = client.post(f"/workflows/{workflow_id}/plan")
    assert plan.status_code == 200, plan.text
    plan_body = plan.json()
    assert plan_body["used_mock"] is True
    assert len(plan_body["steps"]) >= 3
    assert plan_body["steps"][0]["tool_name"] in {
        "mock_web_search_tool",
        "summarize_text_tool",
        "create_todo_list_tool",
        "generate_markdown_report_tool",
        "extract_key_points_tool",
    }

    detail = client.get(f"/workflows/{workflow_id}").json()
    assert detail["status"] == "planned"
    assert detail["step_count"] == len(plan_body["steps"])

    approve = client.post(f"/workflows/{workflow_id}/approve")
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    execute = client.post(f"/workflows/{workflow_id}/execute")
    assert execute.status_code == 200, execute.text
    executed = execute.json()
    assert executed["status"] == "completed"
    assert all(step["status"] == "succeeded" for step in executed["steps"])

    report = client.get(f"/workflows/{workflow_id}/report")
    assert report.status_code == 200
    md = report.json()["markdown"]
    assert md.startswith("# ")


def test_reject_blocks_execution(client: TestClient) -> None:
    workflow = _create_workflow(client)
    wid = workflow["id"]
    client.post(f"/workflows/{wid}/plan")
    rejected = client.post(f"/workflows/{wid}/reject")
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    execute = client.post(f"/workflows/{wid}/execute")
    assert execute.status_code == 409


def test_cannot_execute_a_draft_workflow(client: TestClient) -> None:
    workflow = _create_workflow(client)
    response = client.post(f"/workflows/{workflow['id']}/execute")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "invalid_state"


def test_get_unknown_workflow_returns_404(client: TestClient) -> None:
    response = client.get("/workflows/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_stats_endpoint_reflects_lifecycle(client: TestClient) -> None:
    initial = client.get("/workflows/stats").json()
    assert initial["total"] == 0

    workflow = _create_workflow(client)
    wid = workflow["id"]
    client.post(f"/workflows/{wid}/plan")

    after_plan = client.get("/workflows/stats").json()
    assert after_plan["total"] == 1
    assert after_plan["awaiting_approval"] == 1

    client.post(f"/workflows/{wid}/approve")
    client.post(f"/workflows/{wid}/execute")

    after_exec = client.get("/workflows/stats").json()
    assert after_exec["completed"] == 1
    assert after_exec["awaiting_approval"] == 0


def test_validation_error_on_short_goal(client: TestClient) -> None:
    response = client.post(
        "/workflows", json={"title": "ok title", "goal": "short"}
    )
    assert response.status_code == 422
