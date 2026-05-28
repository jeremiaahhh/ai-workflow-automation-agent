# Tool System

## Why a registry?

The agent's safety properties come from the fact that the LLM cannot invent
new tools at runtime. The executor only ever dispatches through
`ToolRegistry.get(name)`, which looks up tools that the application
**explicitly registered at startup**. A planner that hallucinates a tool name
is rejected before any database write or tool invocation.

## Anatomy of a tool

Every tool is a subclass of `Tool[TInput, TOutput]` with three required pieces:

```python
class SummarizeTextInput(BaseModel):
    text: str = Field(min_length=10, max_length=20_000)
    max_sentences: int = Field(default=3, ge=1, le=10)


class SummarizeTextOutput(BaseModel):
    summary: str
    sentence_count: int
    compression_ratio: float


class SummarizeTextTool(Tool[SummarizeTextInput, SummarizeTextOutput]):
    name = "summarize_text_tool"
    description = "Returns a short summary of the provided text…"
    input_model = SummarizeTextInput
    output_model = SummarizeTextOutput

    def _run(self, args: SummarizeTextInput) -> SummarizeTextOutput:
        ...
```

- `name` — the public identifier, surfaced to the planner.
- `description` — what the tool does, in one paragraph. The planner sees this.
- `input_model` — Pydantic schema. Used both to validate arguments and to
  generate the JSON schema sent to the planner.
- `output_model` — Pydantic schema for the return value. Keeps callers honest.
- `_run` — the actual implementation. Pure function; never raises raw
  exceptions for "expected" failures.

The base class wraps `_run` with timing, exception handling, and uniform
`ToolResult` packaging, so the executor doesn't need to know per-tool details.

## The five registered tools

| Tool                              | Purpose                                                   |
| --------------------------------- | --------------------------------------------------------- |
| `mock_web_search_tool`            | Deterministic seeded mock of a search engine              |
| `summarize_text_tool`             | Frequency-weighted extractive summarization               |
| `create_todo_list_tool`           | Topic-templated action checklist                          |
| `extract_key_points_tool`         | Signal-word + length ranking of source sentences          |
| `generate_markdown_report_tool`   | Builds a polished Markdown report from title + sections   |

All five are deterministic, run locally, never touch the network, and are
covered by `backend/tests/test_tools.py`.

## Registering a new tool

1. **Implement the class.** Subclass `Tool[Input, Output]` with Pydantic
   schemas. Place it in `backend/app/tools/<your_tool>.py`.
2. **Register it.** Add a `registry.register(YourTool())` line inside
   `_build_default_registry` in `backend/app/tools/registry.py`.
3. **Test it.** Add an entry to `tests/test_tools.py` covering at minimum
   a happy path, the deterministic property, and one validation failure.

That's it. The planner will see the new tool the next time `/health` or
`/tools` is hit (the registry is rebuilt on process start).

## Safety checks at the boundary

Before any tool fires, three guards run in this order:

1. **`assert_tool_allowed(name, registered)`** — refuses unknown tool names
   (defensive; the planner is already validated).
2. **`assert_executable_state(status)`** — refuses to run unless the workflow
   is in `approved` or `running` state.
3. **`sanitize_tool_args(args)`** — bounds string length and list size before
   the value crosses into `Tool.invoke()`.

Then `Tool.invoke()`:

4. **Validates the args** against `input_model`. Bad input raises
   `ValidationError` and is recorded as a failed step (`error_message` set,
   `output` null).
5. **Times the run.** `duration_ms` is captured even on failure.
6. **Catches `Exception`** so a buggy tool can't take down the executor — the
   step fails and the workflow moves to `failed`.

## Determinism guarantee

Because every registered tool is deterministic, you can re-run a workflow with
the same arguments and get byte-identical output. This is what makes the mock
demo trustworthy as a portfolio piece: you don't have to apologize for
"sometimes the model says something else."

When the live providers are enabled (`USE_MOCK_AI=false`), determinism is no
longer guaranteed — but the tool outputs themselves stay deterministic.
The only nondeterminism comes from the planner's choice of arguments.

## Threat model (briefly)

The system assumes:

- The operator is willing to approve a plan before it runs.
- The set of registered tools is curated, code-reviewed, and intentionally
  side-effect-free.

Out of scope:

- Tools that touch external systems (databases, payment APIs, deployment
  pipelines). Adding one requires writing it; doing so safely is a separate
  conversation about credentials, scopes, and idempotency.
- Multi-tenant abuse. There is no auth layer — see `docs/architecture.md` for
  the missing pieces.
