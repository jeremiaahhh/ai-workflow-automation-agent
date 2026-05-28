from __future__ import annotations

import re
from typing import ClassVar

from pydantic import BaseModel, Field

from app.tools.base import Tool


class CreateTodoListInput(BaseModel):
    topic: str = Field(min_length=3, max_length=300)
    context: str | None = Field(default=None, max_length=4000)
    max_items: int = Field(default=6, ge=1, le=12)


class TodoItem(BaseModel):
    position: int
    title: str
    detail: str


class CreateTodoListOutput(BaseModel):
    topic: str
    items: list[TodoItem]


_TEMPLATES: list[tuple[str, str]] = [
    ("Define scope and success criteria", "Write down what 'done' looks like for {topic} so later steps can be checked against it."),
    ("Gather background context", "Collect relevant prior work, internal docs, or constraints related to {topic}."),
    ("Identify stakeholders and owners", "List the people who need to review or approve changes to {topic}."),
    ("Draft the initial plan", "Outline the major moves required to deliver {topic} end to end."),
    ("Validate assumptions with a small experiment", "Run the cheapest possible check that would tell you {topic} is on the wrong track."),
    ("Execute the highest-leverage step", "Do the one action that unblocks the most other work on {topic}."),
    ("Review progress and adjust", "Compare actual outcomes against the success criteria and reprioritize remaining work."),
    ("Document and hand off", "Write a short summary so the next person can pick up {topic} without you."),
    ("Schedule a follow-up checkpoint", "Put a reminder on the calendar to revisit {topic} after the first iteration ships."),
    ("Capture lessons learned", "Note what surprised you while working on {topic} so it informs future plans."),
]


class CreateTodoListTool(Tool[CreateTodoListInput, CreateTodoListOutput]):
    name: ClassVar[str] = "create_todo_list_tool"
    description: ClassVar[str] = (
        "Generates an ordered checklist for a given topic. Uses a fixed template "
        "library so the output is deterministic and safe to run without an LLM."
    )
    input_model: ClassVar[type[BaseModel]] = CreateTodoListInput
    output_model: ClassVar[type[BaseModel]] = CreateTodoListOutput

    def _run(self, args: CreateTodoListInput) -> CreateTodoListOutput:
        topic = args.topic.strip().rstrip(".")
        items = [
            TodoItem(
                position=i + 1,
                title=title,
                detail=re.sub(r"\{topic\}", topic, detail),
            )
            for i, (title, detail) in enumerate(_TEMPLATES[: args.max_items])
        ]
        return CreateTodoListOutput(topic=topic, items=items)
