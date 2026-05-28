"use client";

import Link from "next/link";
import { Quote } from "lucide-react";

type Output = Record<string, unknown> | null | undefined;

interface ToolOutputProps {
  toolName: string;
  output: Output;
}

function asString(value: unknown): string {
  return typeof value === "string" ? value : JSON.stringify(value);
}

export function ToolOutput({ toolName, output }: ToolOutputProps) {
  if (!output) {
    return (
      <p className="text-xs italic text-muted-foreground">No output recorded.</p>
    );
  }

  if (toolName === "mock_web_search_tool") {
    const results = (output.results as Array<{
      title: string;
      url: string;
      snippet: string;
    }>) || [];
    if (results.length === 0) {
      return (
        <p className="text-xs italic text-muted-foreground">No results returned.</p>
      );
    }
    return (
      <ul className="space-y-3">
        {results.map((r) => (
          <li key={r.url} className="space-y-1">
            <Link
              href={r.url}
              target="_blank"
              rel="noreferrer"
              className="text-sm font-medium text-primary hover:underline"
            >
              {r.title}
            </Link>
            <p className="text-xs text-muted-foreground">{r.url}</p>
            <p className="text-sm text-foreground/90">{r.snippet}</p>
          </li>
        ))}
      </ul>
    );
  }

  if (toolName === "summarize_text_tool") {
    return (
      <blockquote className="relative rounded-lg border-l-4 border-primary/40 bg-primary/5 px-4 py-3 text-sm">
        <Quote className="absolute right-3 top-3 h-3.5 w-3.5 text-primary/60" />
        {asString(output.summary)}
      </blockquote>
    );
  }

  if (toolName === "extract_key_points_tool") {
    const points = (output.points as Array<{ position: number; text: string }>) || [];
    return (
      <ul className="space-y-2">
        {points.map((p) => (
          <li key={p.position} className="flex gap-2 text-sm">
            <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[11px] font-semibold text-primary">
              {p.position}
            </span>
            <span className="text-foreground/90">{p.text}</span>
          </li>
        ))}
      </ul>
    );
  }

  if (toolName === "create_todo_list_tool") {
    const items =
      (output.items as Array<{
        position: number;
        title: string;
        detail: string;
      }>) || [];
    return (
      <ol className="space-y-3">
        {items.map((item) => (
          <li
            key={item.position}
            className="rounded-lg border bg-background p-3 text-sm"
          >
            <p className="font-medium">
              {item.position}. {item.title}
            </p>
            <p className="mt-1 text-muted-foreground">{item.detail}</p>
          </li>
        ))}
      </ol>
    );
  }

  if (toolName === "generate_markdown_report_tool") {
    return (
      <pre className="max-h-72 overflow-auto rounded-lg border bg-muted/40 p-3 text-xs leading-relaxed">
        {asString(output.markdown)}
      </pre>
    );
  }

  return (
    <pre className="max-h-72 overflow-auto rounded-lg border bg-muted/40 p-3 text-xs">
      {JSON.stringify(output, null, 2)}
    </pre>
  );
}
