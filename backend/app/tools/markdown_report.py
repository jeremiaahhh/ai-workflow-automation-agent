from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, Field

from app.tools.base import Tool


class ReportSection(BaseModel):
    heading: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=8000)


class GenerateMarkdownReportInput(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    summary: str = Field(min_length=10, max_length=4000)
    sections: list[ReportSection] = Field(default_factory=list, max_length=10)
    bullets: list[str] = Field(default_factory=list, max_length=20)


class GenerateMarkdownReportOutput(BaseModel):
    markdown: str
    word_count: int
    section_count: int


class GenerateMarkdownReportTool(
    Tool[GenerateMarkdownReportInput, GenerateMarkdownReportOutput]
):
    name: ClassVar[str] = "generate_markdown_report_tool"
    description: ClassVar[str] = (
        "Renders a polished Markdown report from a title, summary, optional "
        "sections, and bullet highlights. Deterministic; no network access."
    )
    input_model: ClassVar[type[BaseModel]] = GenerateMarkdownReportInput
    output_model: ClassVar[type[BaseModel]] = GenerateMarkdownReportOutput

    def _run(
        self, args: GenerateMarkdownReportInput
    ) -> GenerateMarkdownReportOutput:
        parts: list[str] = [f"# {args.title}", "", "## Summary", "", args.summary.strip()]
        if args.bullets:
            parts += ["", "## Highlights", ""]
            for bullet in args.bullets:
                bullet = bullet.strip()
                if bullet:
                    parts.append(f"- {bullet}")
        for section in args.sections:
            parts += ["", f"## {section.heading.strip()}", "", section.body.strip()]
        markdown = "\n".join(parts).strip() + "\n"
        word_count = len(markdown.split())
        return GenerateMarkdownReportOutput(
            markdown=markdown,
            word_count=word_count,
            section_count=len(args.sections),
        )
