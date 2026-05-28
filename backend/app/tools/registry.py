from __future__ import annotations

from app.core.errors import ToolNotFoundError
from app.schemas.tool import ToolDefinition
from app.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(
                f"Tool '{name}' is not registered.",
                details={"available_tools": sorted(self._tools)},
            ) from exc

    def names(self) -> set[str]:
        return set(self._tools)

    def definitions(self) -> list[ToolDefinition]:
        return [t.definition() for t in self._tools.values()]


def _build_default_registry() -> ToolRegistry:
    # Imports are local to keep this module side-effect-free at import time
    # (the registry is intentionally explicit).
    from app.tools.create_todo_list import CreateTodoListTool
    from app.tools.extract_key_points import ExtractKeyPointsTool
    from app.tools.markdown_report import GenerateMarkdownReportTool
    from app.tools.mock_web_search import MockWebSearchTool
    from app.tools.summarize_text import SummarizeTextTool

    registry = ToolRegistry()
    registry.register(MockWebSearchTool())
    registry.register(SummarizeTextTool())
    registry.register(CreateTodoListTool())
    registry.register(GenerateMarkdownReportTool())
    registry.register(ExtractKeyPointsTool())
    return registry


default_registry: ToolRegistry = _build_default_registry()
