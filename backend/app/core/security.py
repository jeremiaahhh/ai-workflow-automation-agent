"""Safety checks for agent tool execution.

The agent only invokes tools through the registry, so a step is allowed only
when (a) the tool exists, (b) the workflow is in a state that permits
execution, and (c) the provided arguments validate against the tool's Pydantic
input schema. These checks are deliberately conservative — better to refuse
ambiguous input than to let an unbounded loop run.
"""

from __future__ import annotations

from typing import Any

from app.core.errors import InvalidStateError, ToolNotFoundError, ValidationError


MAX_STRING_INPUT = 20_000
MAX_LIST_ITEMS = 200


def assert_tool_allowed(tool_name: str, registered_tools: set[str]) -> None:
    if tool_name not in registered_tools:
        raise ToolNotFoundError(
            f"Tool '{tool_name}' is not registered.",
            details={"available_tools": sorted(registered_tools)},
        )


def assert_executable_state(current_status: str) -> None:
    if current_status not in {"approved", "running"}:
        raise InvalidStateError(
            f"Workflow cannot be executed from status '{current_status}'.",
            details={"required_status": ["approved", "running"]},
        )


def sanitize_tool_args(args: dict[str, Any]) -> dict[str, Any]:
    """Defensive bounds for free-form tool arguments before invocation."""
    if not isinstance(args, dict):
        raise ValidationError("Tool arguments must be a JSON object.")
    cleaned: dict[str, Any] = {}
    for key, value in args.items():
        if isinstance(value, str):
            if len(value) > MAX_STRING_INPUT:
                raise ValidationError(
                    f"Argument '{key}' exceeds the {MAX_STRING_INPUT}-character limit."
                )
            cleaned[key] = value
        elif isinstance(value, list):
            if len(value) > MAX_LIST_ITEMS:
                raise ValidationError(
                    f"Argument '{key}' exceeds the {MAX_LIST_ITEMS}-item limit."
                )
            cleaned[key] = value
        else:
            cleaned[key] = value
    return cleaned
