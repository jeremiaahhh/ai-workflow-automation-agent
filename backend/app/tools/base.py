from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import BaseModel, ValidationError as PydanticValidationError

from app.core.errors import ToolExecutionError, ValidationError
from app.schemas.tool import ToolDefinition, ToolResult

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class Tool(ABC, Generic[TInput, TOutput]):
    """Abstract base for a registered tool.

    Subclasses define a Pydantic input + output schema and implement `_run`.
    `invoke` wraps execution with input validation, timing, and uniform
    `ToolResult` packaging so the executor doesn't need to know per-tool details.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    input_model: ClassVar[type[BaseModel]]
    output_model: ClassVar[type[BaseModel]]

    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.name,
            description=cls.description,
            input_schema=cls.input_model.model_json_schema(),
        )

    def invoke(self, raw_args: dict[str, Any]) -> ToolResult:
        try:
            args = self.input_model.model_validate(raw_args)
        except PydanticValidationError as exc:
            raise ValidationError(
                f"Invalid arguments for tool '{self.name}'.",
                details={"errors": exc.errors()},
            ) from exc

        start = time.perf_counter()
        try:
            output: BaseModel = self._run(args)  # type: ignore[arg-type]
        except ToolExecutionError:
            raise
        except Exception as exc:  # noqa: BLE001
            duration_ms = int((time.perf_counter() - start) * 1000)
            return ToolResult(success=False, error=str(exc), duration_ms=duration_ms)

        duration_ms = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            success=True,
            output=output.model_dump(mode="json"),
            duration_ms=duration_ms,
        )

    @abstractmethod
    def _run(self, args: TInput) -> TOutput:  # pragma: no cover - abstract
        ...
