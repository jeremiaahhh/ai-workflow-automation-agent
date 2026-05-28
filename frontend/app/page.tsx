"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Clock,
  ListChecks,
  PlusCircle,
  Workflow as WorkflowIcon,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/empty-state";
import { StatCard } from "@/components/stat-card";
import { StatusBadge } from "@/components/status-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { formatDateTime, relativeTime } from "@/lib/utils";
import type { WorkflowStats, WorkflowSummary } from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<WorkflowStats | null>(null);
  const [recent, setRecent] = useState<WorkflowSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.stats(), api.listWorkflows()])
      .then(([s, list]) => {
        if (cancelled) return;
        setStats(s);
        setRecent(list.slice(0, 6));
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
      <section className="relative overflow-hidden rounded-2xl border bg-card p-8 shadow-sm">
        <div className="grid-bg absolute inset-0 opacity-40" />
        <div className="relative grid gap-6 lg:grid-cols-[1.4fr_1fr] lg:items-center">
          <div className="space-y-4">
            <span className="inline-flex items-center gap-2 rounded-full border bg-background px-3 py-1 text-xs font-medium shadow-sm">
              <CheckCircle2 className="h-3.5 w-3.5 text-primary" />
              Plan → Approve → Execute
            </span>
            <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
              A typed <span className="gradient-text">agent runtime</span>
              <br className="hidden md:block" />
              for safe, auditable workflows.
            </h1>
            <p className="max-w-xl text-sm leading-relaxed text-muted-foreground">
              Forge Agent turns a goal into a typed, human-approved plan, executes it
              through a fixed catalog of registered tools, and produces a Markdown
              report you can ship. Every step is logged, timed, and reversible.
            </p>
            <div className="flex flex-wrap gap-2">
              <Button asChild>
                <Link href="/workflows/new">
                  <PlusCircle className="h-4 w-4" />
                  Start a workflow
                </Link>
              </Button>
              <Button asChild variant="outline">
                <Link href="/workflows">
                  <ListChecks className="h-4 w-4" />
                  Browse history
                </Link>
              </Button>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="rounded-xl border bg-background/80 p-4 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Sample plan
              </p>
              <ol className="mt-3 space-y-2 text-sm">
                {[
                  { tool: "mock_web_search_tool", desc: "Gather background." },
                  { tool: "summarize_text_tool", desc: "Briefing." },
                  { tool: "extract_key_points_tool", desc: "Key takeaways." },
                  { tool: "create_todo_list_tool", desc: "Action plan." },
                  { tool: "generate_markdown_report_tool", desc: "Final report." },
                ].map((s, i) => (
                  <li key={s.tool} className="flex items-start gap-2.5">
                    <span className="mt-0.5 inline-flex h-5 w-5 items-center justify-center rounded-full bg-primary/15 text-[11px] font-semibold text-primary">
                      {i + 1}
                    </span>
                    <div className="min-w-0">
                      <code className="rounded bg-muted px-1.5 py-0.5 text-[11px]">
                        {s.tool}
                      </code>
                      <p className="mt-1 text-xs text-muted-foreground">{s.desc}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {stats ? (
          <>
            <StatCard
              label="Total workflows"
              value={stats.total}
              icon={WorkflowIcon}
              tone="primary"
            />
            <StatCard
              label="Awaiting approval"
              value={stats.awaiting_approval}
              icon={Clock}
              tone="warning"
              hint="Plans ready for review"
            />
            <StatCard
              label="Running"
              value={stats.running}
              icon={Activity}
              tone="primary"
            />
            <StatCard
              label="Completed"
              value={stats.completed}
              icon={CheckCircle2}
              tone="success"
            />
            <StatCard
              label="Failed"
              value={stats.failed}
              icon={XCircle}
              tone="danger"
            />
          </>
        ) : error ? (
          <Card className="md:col-span-2 xl:col-span-5">
            <CardContent className="py-6 text-sm text-rose-600">
              Could not reach the backend: {error}
            </CardContent>
          </Card>
        ) : (
          Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full" />
          ))
        )}
      </section>

      <section>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <div className="space-y-1">
              <CardTitle>Recent workflows</CardTitle>
              <p className="text-xs text-muted-foreground">
                Most recently created — newest first
              </p>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/workflows">View all</Link>
            </Button>
          </CardHeader>
          <CardContent>
            {recent == null ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <Skeleton key={i} className="h-14 w-full" />
                ))}
              </div>
            ) : recent.length === 0 ? (
              <EmptyState
                icon={WorkflowIcon}
                title="No workflows yet"
                description="Create your first workflow to see the planner in action — runs offline in mock mode by default."
                action={
                  <Button asChild>
                    <Link href="/workflows/new">
                      <PlusCircle className="h-4 w-4" />
                      Create workflow
                    </Link>
                  </Button>
                }
              />
            ) : (
              <ul className="divide-y">
                {recent.map((wf) => (
                  <li key={wf.id}>
                    <Link
                      href={`/workflows/${wf.id}`}
                      className="flex items-center justify-between gap-4 py-3 transition-colors hover:bg-accent/40 -mx-3 px-3 rounded-lg"
                    >
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">{wf.title}</p>
                        <p className="truncate text-xs text-muted-foreground">
                          {wf.goal}
                        </p>
                      </div>
                      <div className="flex shrink-0 items-center gap-3">
                        <span className="hidden text-xs text-muted-foreground sm:inline">
                          {relativeTime(wf.created_at)}
                        </span>
                        <span
                          className="hidden text-xs text-muted-foreground md:inline"
                          title={formatDateTime(wf.created_at)}
                        >
                          {wf.completed_steps}/{wf.step_count} steps
                        </span>
                        <StatusBadge status={wf.status} />
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </section>
    </>
  );
}
