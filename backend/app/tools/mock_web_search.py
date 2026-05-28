from __future__ import annotations

import hashlib
from typing import ClassVar

from pydantic import BaseModel, Field

from app.tools.base import Tool


class MockWebSearchInput(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    max_results: int = Field(default=5, ge=1, le=10)


class MockSearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class MockWebSearchOutput(BaseModel):
    query: str
    results: list[MockSearchResult]


_CORPUS: list[tuple[str, str, str]] = [
    (
        "State of AI agents in 2026",
        "https://example.com/ai-agents-2026",
        "Tooling around agentic systems has matured around plan-then-execute patterns with explicit human approval gates.",
    ),
    (
        "How to structure agent tool registries",
        "https://example.com/tool-registry-patterns",
        "Centralized tool registries with typed input schemas and per-tool quotas are the dominant pattern across production agents.",
    ),
    (
        "Designing safe autonomous workflows",
        "https://example.com/safe-autonomy",
        "Workflows scoped to a fixed set of side-effect-free tools are dramatically easier to operate than open-ended agents.",
    ),
    (
        "Markdown reports for AI workflows",
        "https://example.com/markdown-reports",
        "Generating a final markdown report from each run helps operators audit decisions and re-run with new context.",
    ),
    (
        "Why human-in-the-loop still wins",
        "https://example.com/human-in-the-loop",
        "Plan approval steps reduce cost and incident rate without meaningfully slowing iteration.",
    ),
    (
        "Patterns for agent observability",
        "https://example.com/agent-observability",
        "Per-step structured logs and timing data are table stakes for understanding agent behavior.",
    ),
    (
        "Picking an LLM provider abstraction",
        "https://example.com/llm-abstraction",
        "A thin provider interface that returns plain strings beats heavyweight frameworks for most apps.",
    ),
]


class MockWebSearchTool(Tool[MockWebSearchInput, MockWebSearchOutput]):
    name: ClassVar[str] = "mock_web_search_tool"
    description: ClassVar[str] = (
        "Deterministic mock of a web search engine. Returns up to `max_results` "
        "ranked results from a fixed corpus seeded by the query string. Used so "
        "the agent can be demoed end-to-end without external network access."
    )
    input_model: ClassVar[type[BaseModel]] = MockWebSearchInput
    output_model: ClassVar[type[BaseModel]] = MockWebSearchOutput

    def _run(self, args: MockWebSearchInput) -> MockWebSearchOutput:
        seed = int(hashlib.sha256(args.query.lower().encode()).hexdigest(), 16)
        rotated = _CORPUS[seed % len(_CORPUS):] + _CORPUS[: seed % len(_CORPUS)]
        results = [
            MockSearchResult(title=title, url=url, snippet=snippet)
            for title, url, snippet in rotated[: args.max_results]
        ]
        return MockWebSearchOutput(query=args.query, results=results)
