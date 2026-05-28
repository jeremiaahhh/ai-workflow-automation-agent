"use client";

import { ChevronDown, ChevronRight, AlertCircle } from "lucide-react";
import { useState } from "react";
import { StatusBadge } from "@/components/status-badge";
import { ToolOutput } from "@/components/workflow/tool-output";
import { cn, formatDuration } from "@/lib/utils";
import type { ExecutionStep } from "@/lib/types";

interface Props {
  steps: ExecutionStep[];
}

export function ExecutionTimeline({ steps }: Props) {
  const [open, setOpen] = useState<Set<string>>(() => new Set(steps.map((s) => s.id)));

  const toggle = (id: string) => {
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <ol className="relative space-y-4 pl-6">
      <span
        aria-hidden
        className="absolute bottom-2 left-[11px] top-2 w-px bg-gradient-to-b from-border via-border to-transparent"
      />
      {steps.map((step) => {
        const expanded = open.has(step.id);
        return (
          <li key={step.id} className="relative">
            <span
              aria-hidden
              className={cn(
                "absolute -left-6 top-3 flex h-6 w-6 items-center justify-center rounded-full border-2 border-background bg-card text-[11px] font-semibold shadow-sm ring-1 ring-border",
                step.status === "succeeded" && "text-emerald-600 ring-emerald-300",
                step.status === "failed" && "text-rose-600 ring-rose-300",
                step.status === "running" && "text-amber-600 ring-amber-300",
              )}
            >
              {step.position}
            </span>
            <div className="rounded-xl border bg-card shadow-sm">
              <button
                type="button"
                onClick={() => toggle(step.id)}
                className="flex w-full items-start justify-between gap-4 p-4 text-left"
              >
                <div className="min-w-0 flex-1 space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <code className="rounded bg-muted px-1.5 py-0.5 text-xs font-medium">
                      {step.tool_name}
                    </code>
                    <StatusBadge status={step.status} variant="step" />
                    <span className="text-xs text-muted-foreground">
                      {formatDuration(step.duration_ms)}
                    </span>
                  </div>
                  <p className="text-sm text-foreground/90">{step.description}</p>
                </div>
                {expanded ? (
                  <ChevronDown className="mt-0.5 h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="mt-0.5 h-4 w-4 text-muted-foreground" />
                )}
              </button>
              {expanded && (
                <div className="border-t bg-background/50 p-4">
                  <div className="mb-4 space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Arguments
                    </p>
                    <pre className="max-h-56 overflow-auto rounded-lg border bg-muted/40 p-3 text-xs">
                      {JSON.stringify(step.arguments, null, 2)}
                    </pre>
                  </div>
                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Output
                    </p>
                    {step.error_message ? (
                      <div className="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
                        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                        <span>{step.error_message}</span>
                      </div>
                    ) : (
                      <ToolOutput toolName={step.tool_name} output={step.output} />
                    )}
                  </div>
                </div>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
