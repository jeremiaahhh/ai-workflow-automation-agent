from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_ok_and_registered_tools(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["mock_mode"] is True
    assert "mock_web_search_tool" in body["registered_tools"]


def test_list_tools_returns_all_definitions(client: TestClient) -> None:
    response = client.get("/tools")
    assert response.status_code == 200
    names = {tool["name"] for tool in response.json()}
    assert names == {
        "mock_web_search_tool",
        "summarize_text_tool",
        "create_todo_list_tool",
        "generate_markdown_report_tool",
        "extract_key_points_tool",
    }
