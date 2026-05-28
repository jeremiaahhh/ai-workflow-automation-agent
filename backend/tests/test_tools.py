from __future__ import annotations

import pytest

from app.core.errors import ValidationError
from app.tools.create_todo_list import CreateTodoListTool
from app.tools.extract_key_points import ExtractKeyPointsTool
from app.tools.markdown_report import GenerateMarkdownReportTool
from app.tools.mock_web_search import MockWebSearchTool
from app.tools.registry import default_registry
from app.tools.summarize_text import SummarizeTextTool


def test_registry_exposes_all_five_tools() -> None:
    expected = {
        "mock_web_search_tool",
        "summarize_text_tool",
        "create_todo_list_tool",
        "generate_markdown_report_tool",
        "extract_key_points_tool",
    }
    assert default_registry.names() == expected
    definitions = {d.name for d in default_registry.definitions()}
    assert definitions == expected


def test_mock_web_search_is_deterministic_for_same_query() -> None:
    tool = MockWebSearchTool()
    first = tool.invoke({"query": "agent design", "max_results": 3})
    second = tool.invoke({"query": "agent design", "max_results": 3})
    assert first.success and second.success
    assert first.output == second.output
    assert len(first.output["results"]) == 3


def test_summarize_text_returns_shorter_text() -> None:
    text = (
        "Agentic systems benefit from plan-then-execute loops. "
        "A human approval step prevents most large-cost incidents. "
        "Tool registries with typed input schemas make agents auditable. "
        "Structured logs give operators per-step timing data."
    )
    result = SummarizeTextTool().invoke({"text": text, "max_sentences": 2})
    assert result.success
    assert result.output["sentence_count"] <= 2
    assert len(result.output["summary"]) < len(text)


def test_todo_list_renders_topic_in_each_item() -> None:
    result = CreateTodoListTool().invoke(
        {"topic": "Migrate to Postgres 16", "max_items": 4}
    )
    assert result.success
    items = result.output["items"]
    assert len(items) == 4
    assert all("Migrate to Postgres 16" in item["detail"] for item in items)


def test_extract_key_points_orders_by_source_position() -> None:
    text = (
        "Plan approval steps are critical for safety. "
        "Tools must always validate their inputs. "
        "Reports help operators audit each run. "
        "Pleasant weather today."
    )
    result = ExtractKeyPointsTool().invoke({"text": text, "max_points": 3})
    assert result.success
    points = result.output["points"]
    assert len(points) == 3
    assert points[0]["position"] == 1
    assert all("position" in p for p in points)


def test_generate_markdown_report_has_required_sections() -> None:
    result = GenerateMarkdownReportTool().invoke(
        {
            "title": "Quarterly Review",
            "summary": "Findings from running the agent on a research goal.",
            "bullets": ["bullet one", "bullet two"],
            "sections": [{"heading": "Findings", "body": "Some findings."}],
        }
    )
    assert result.success
    md = result.output["markdown"]
    assert md.startswith("# Quarterly Review")
    assert "## Summary" in md
    assert "## Findings" in md
    assert "- bullet one" in md


def test_tool_validation_error_raises_app_error() -> None:
    with pytest.raises(ValidationError):
        SummarizeTextTool().invoke({"text": "x"})  # too short
