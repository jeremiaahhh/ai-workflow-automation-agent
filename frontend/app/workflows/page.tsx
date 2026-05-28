"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ListChecks, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/status-badge";
import { api } from "@/lib/api";
import { formatDateTime, relativeTime } from "@/lib/utils";
import type { WorkflowSummary } from "@/lib/types";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listWorkflows()
      .then(setWorkflows)
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <>
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">Workflows</h1>
          <p className="text-sm text-muted-foreground">
            Every workflow you’ve drafted, planned, or run — newest first.
          </p>
        </div>
        <Button asChild>
          <Link href="/workflows/new">
            <PlusCircle className="h-4 w-4" />
            New workflow
          </Link>
        </Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>History</CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <p className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
              Couldn’t load workflows: {error}
            </p>
          ) : workflows == null ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-14 w-full" />
              ))}
            </div>
          ) : workflows.length === 0 ? (
            <EmptyState
              icon={ListChecks}
              title="No workflows yet"
              description="Create your first one — the planner runs offline in mock mode by default."
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
            <div className="overflow-hidden rounded-lg border">
              <table className="min-w-full divide-y text-sm">
                <thead className="bg-muted/40 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 text-left">Workflow</th>
                    <th className="hidden px-4 py-3 text-left md:table-cell">
                      Created
                    </th>
                    <th className="hidden px-4 py-3 text-left lg:table-cell">
                      Steps
                    </th>
                    <th className="px-4 py-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y bg-card">
                  {workflows.map((wf) => (
                    <tr
                      key={wf.id}
                      className="cursor-pointer transition-colors hover:bg-accent/30"
                    >
                      <td className="px-4 py-3">
                        <Link
                          href={`/workflows/${wf.id}`}
                          className="block max-w-md"
                        >
                          <p className="truncate font-medium">{wf.title}</p>
                          <p className="truncate text-xs text-muted-foreground">
                            {wf.goal}
                          </p>
                        </Link>
                      </td>
                      <td
                        className="hidden whitespace-nowrap px-4 py-3 text-xs text-muted-foreground md:table-cell"
                        title={formatDateTime(wf.created_at)}
                      >
                        {relativeTime(wf.created_at)}
                      </td>
                      <td className="hidden whitespace-nowrap px-4 py-3 text-xs text-muted-foreground lg:table-cell">
                        {wf.completed_steps}/{wf.step_count}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-right">
                        <StatusBadge status={wf.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );
}
