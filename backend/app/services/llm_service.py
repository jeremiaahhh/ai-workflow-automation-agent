"""LLM provider abstraction.

The agent only needs one capability from the LLM: take a goal + the catalog of
available tools and return a structured plan (`AgentPlan`). To keep the rest of
the system testable, that capability lives behind `PlanGenerator` with three
implementations:

- `MockPlanGenerator` — deterministic heuristics keyed off the goal text.
  Always available, no API key required, used in CI and local demos.
- `OpenAIPlanGenerator` — calls `openai.chat.completions.create` and asks for
  a JSON response that matches `AgentPlan`.
- `AnthropicPlanGenerator` — same shape, against the Anthropic Messages API.

Selection happens in `get_plan_generator()` based on `Settings`. The factory
silently downgrades to the mock when an API key is missing, which is how the
"runs without a key" promise is kept.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.schemas.agent import AgentPlan, PlannedStep
from app.schemas.tool import ToolDefinition

logger = get_logger(__name__)


_SYSTEM_PROMPT = (
    "You are an AI workflow planner. Given a user goal and a catalog of allowed "
    "tools, produce a short ordered plan (no more than the requested maximum) "
    "describing which tool to invoke at each step and why. You may ONLY use the "
    "listed tools. Respond with JSON matching this schema strictly:\n"
    '{"rationale": str, "steps": [{"position": int, "tool_name": str, '
    '"description": str, "arguments": object}]}'
)


def _format_tool_catalog(tools: list[ToolDefinition]) -> str:
    rendered = []
    for tool in tools:
        rendered.append(
            f"- {tool.name}: {tool.description}\n  input_schema: {json.dumps(tool.input_schema)}"
        )
    return "\n".join(rendered)


class PlanGenerator(ABC):
    is_mock: bool = False

    @abstractmethod
    def generate(
        self,
        *,
        workflow_id: str,
        goal: str,
        context: str | None,
        tools: list[ToolDefinition],
        max_steps: int,
    ) -> AgentPlan: ...


class MockPlanGenerator(PlanGenerator):
    is_mock = True

    def generate(
        self,
        *,
        workflow_id: str,
        goal: str,
        context: str | None,
        tools: list[ToolDefinition],
        max_steps: int,
    ) -> AgentPlan:
        tool_names = {t.name for t in tools}
        steps: list[PlannedStep] = []
        position = 1
        topic = goal.strip().rstrip(".")
        short_topic = topic if len(topic) <= 80 else topic[:77] + "…"

        if "mock_web_search_tool" in tool_names:
            steps.append(
                PlannedStep(
                    position=position,
                    tool_name="mock_web_search_tool",
                    description=f"Gather background information about: {short_topic}",
                    arguments={"query": short_topic, "max_results": 5},
                )
            )
            position += 1

        seed_text = self._seed_text(goal, context)

        if "summarize_text_tool" in tool_names:
            steps.append(
                PlannedStep(
                    position=position,
                    tool_name="summarize_text_tool",
                    description="Condense the gathered material into a short briefing.",
                    arguments={"text": seed_text, "max_sentences": 3},
                )
            )
            position += 1

        if "extract_key_points_tool" in tool_names:
            steps.append(
                PlannedStep(
                    position=position,
                    tool_name="extract_key_points_tool",
                    description="Extract the most important takeaways from the briefing.",
                    arguments={"text": seed_text, "max_points": 5},
                )
            )
            position += 1

        if "create_todo_list_tool" in tool_names:
            steps.append(
                PlannedStep(
                    position=position,
                    tool_name="create_todo_list_tool",
                    description=f"Generate an actionable to-do list for: {short_topic}",
                    arguments={"topic": short_topic, "max_items": 6},
                )
            )
            position += 1

        if "generate_markdown_report_tool" in tool_names:
            steps.append(
                PlannedStep(
                    position=position,
                    tool_name="generate_markdown_report_tool",
                    description="Compile a final Markdown report with findings and next steps.",
                    arguments={
                        "title": topic.title() if len(topic) < 80 else "Workflow Report",
                        "summary": (
                            "An end-to-end agent run covering research, key points, "
                            "and an action plan for the stated goal."
                        ),
                        "sections": [],
                        "bullets": [],
                    },
                )
            )

        if len(steps) > max_steps:
            steps = steps[:max_steps]
            for new_pos, step in enumerate(steps, start=1):
                step.position = new_pos

        rationale = (
            "Mock planner: research → summarize → extract key points → plan → report. "
            "This sequence is safe to run offline and exercises every registered tool."
        )
        return AgentPlan(
            workflow_id=workflow_id, rationale=rationale, steps=steps, used_mock=True
        )

    @staticmethod
    def _seed_text(goal: str, context: str | None) -> str:
        base = (
            f"Goal: {goal.strip()}\n\n"
            "Effective agentic systems combine narrow, well-typed tools with a "
            "deterministic plan-then-execute loop. Human approval between "
            "planning and execution is a small cost that prevents most large "
            "incidents. A final Markdown report makes each run auditable and "
            "easy to re-run with new context. Observability requires per-step "
            "structured logs, timing data, and explicit success or failure "
            "transitions."
        )
        if context:
            return f"{base}\n\nUser context: {context.strip()}"
        return base


class OpenAIPlanGenerator(PlanGenerator):
    def __init__(self, settings: Settings) -> None:
        from openai import OpenAI  # imported lazily

        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    def generate(
        self,
        *,
        workflow_id: str,
        goal: str,
        context: str | None,
        tools: list[ToolDefinition],
        max_steps: int,
    ) -> AgentPlan:
        user_prompt = (
            f"Goal: {goal}\n"
            f"Context: {context or 'n/a'}\n"
            f"Max steps: {max_steps}\n\n"
            f"Allowed tools:\n{_format_tool_catalog(tools)}"
        )
        response = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        raw = response.choices[0].message.content or "{}"
        return _parse_plan(workflow_id=workflow_id, raw=raw, used_mock=False)


class AnthropicPlanGenerator(PlanGenerator):
    def __init__(self, settings: Settings) -> None:
        from anthropic import Anthropic  # imported lazily

        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    def generate(
        self,
        *,
        workflow_id: str,
        goal: str,
        context: str | None,
        tools: list[ToolDefinition],
        max_steps: int,
    ) -> AgentPlan:
        user_prompt = (
            f"Goal: {goal}\n"
            f"Context: {context or 'n/a'}\n"
            f"Max steps: {max_steps}\n\n"
            f"Allowed tools:\n{_format_tool_catalog(tools)}"
        )
        message = self._client.messages.create(
            model=self._model,
            max_tokens=1500,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw_text = "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        )
        return _parse_plan(workflow_id=workflow_id, raw=raw_text, used_mock=False)


def _parse_plan(*, workflow_id: str, raw: str, used_mock: bool) -> AgentPlan:
    data: dict[str, Any]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("LLM response did not contain JSON.")
        data = json.loads(raw[start : end + 1])
    steps = [PlannedStep(**s) for s in data.get("steps", [])]
    return AgentPlan(
        workflow_id=workflow_id,
        rationale=data.get("rationale", "").strip() or "No rationale provided.",
        steps=steps,
        used_mock=used_mock,
    )


def get_plan_generator(settings: Settings | None = None) -> PlanGenerator:
    settings = settings or get_settings()
    if settings.is_mock_mode:
        return MockPlanGenerator()
    try:
        if settings.ai_provider == "anthropic":
            return AnthropicPlanGenerator(settings)
        return OpenAIPlanGenerator(settings)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "plan_generator_init_failed_falling_back_to_mock", error=str(exc)
        )
        return MockPlanGenerator()
