"use client";

import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  CircleAlert,
  Download,
  PlayCircle,
  RotateCw,
  Play,
} from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { StatusBadge } from "@/components/status-badge";
import { ExecutionTimeline } from "@/components/workflow/execution-timeline";
import { MarkdownViewer } from "@/components/workflow/markdown-viewer";
import { PlanReview } from "@/components/workflow/plan-review";
import { api, ApiRequestError } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";
import type { AgentPlan, ReportResponse, WorkflowDetail } from "@/lib/types";

export default function WorkflowDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = params.id;

  const [workflow, setWorkflow] = useState<WorkflowDetail | null>(null);
  const [plan, setPlan] = useState<AgentPlan | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<null | "plan" | "approve" | "reject" | "execute">(null);

  const refresh = useCallback(async () => {
    try {
      const wf = await api.getWorkflow(id);
      setWorkflow(wf);
      if (
        wf.status === "completed" ||
        wf.status === "failed" ||
        wf.report_markdown
      ) {
        try {
          setReport(await api.getReport(id));
        } catch {
          // report optional
        }
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handlePlan = async () => {
    setBusy("plan");
    try {
      const p = await api.planWorkflow(id);
      setPlan(p);
      await refresh();
      toast.success("Plan generated.");
    } catch (e) {
      toast.error(
        e instanceof ApiRequestError ? e.message : (e as Error).message,
      );
    } finally {
      setBusy(null);
    }
  };

  const handleApproveAndExecute = async () => {
    setBusy("approve");
    try {
      await api.approveWorkflow(id);
      setBusy("execute");
      const executed = await api.executeWorkflow(id);
      setWorkflow(executed);
      const r = await api.getReport(id);
      setReport(r);
      if (executed.status === "completed") {
        toast.success("Workflow completed.");
      } else {
        toast.error("Execution finished with errors.");
      }
    } catch (e) {
      toast.error(
        e instanceof ApiRequestError ? e.message : (e as Error).message,
      );
      await refresh();
    } finally {
      setBusy(null);
    }
  };

  const handleReject = async () => {
    setBusy("reject");
    try {
      await api.rejectWorkflow(id);
      setPlan(null);
      await refresh();
      toast.success("Plan rejected.");
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusy(null);
    }
  };

  if (error) {
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
        Couldn’t load workflow: {error}
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-9 w-48" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  const progress =
    workflow.step_count === 0
      ? 0
      : Math.round((workflow.completed_steps / workflow.step_count) * 100);

  const showPlanReview = workflow.status === "planned" && workflow.steps.length > 0;
  const hasSteps = workflow.steps.length > 0;

  return (
    <>
      <Button
        asChild
        variant="ghost"
        size="sm"
        className="-ml-2 w-fit text-muted-foreground"
      >
        <Link href="/workflows">
          <ArrowLeft className="h-4 w-4" />
          Back to workflows
        </Link>
      </Button>

      <header className="space-y-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1.5">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold tracking-tight">
                {workflow.title}
              </h1>
              <StatusBadge status={workflow.status} />
            </div>
            <p className="max-w-3xl text-sm text-muted-foreground">
              {workflow.goal}
            </p>
            <p className="text-xs text-muted-foreground">
              Created {formatDateTime(workflow.created_at)} ·{" "}
              {workflow.used_mock ? "Mock planner" : "Live LLM"}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {workflow.status === "draft" && (
              <Button onClick={handlePlan} disabled={busy === "plan"}>
                <Play
                  className={busy === "plan" ? "h-4 w-4 animate-pulse" : "h-4 w-4"}
                />
                {busy === "plan" ? "Planning…" : "Generate plan"}
              </Button>
            )}
            {workflow.status === "rejected" && (
              <Button variant="outline" onClick={handlePlan} disabled={busy === "plan"}>
                <RotateCw className="h-4 w-4" />
                Replan
              </Button>
            )}
            {workflow.status === "approved" && (
              <Button onClick={handleApproveAndExecute} disabled={busy === "execute"}>
                <PlayCircle className="h-4 w-4" />
                {busy === "execute" ? "Executing…" : "Execute now"}
              </Button>
            )}
            <Button variant="outline" size="icon" onClick={refresh} aria-label="Refresh">
              <RotateCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {hasSteps && (
          <Card>
            <CardContent className="flex flex-wrap items-center gap-6 p-4">
              <div className="min-w-0 flex-1 space-y-1.5">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>
                    {workflow.completed_steps} / {workflow.step_count} steps
                    completed
                  </span>
                  <span>{progress}%</span>
                </div>
                <Progress value={progress} />
              </div>
              {workflow.error_message && (
                <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
                  <CircleAlert className="h-4 w-4" />
                  {workflow.error_message}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </header>

      {showPlanReview && (
        <PlanReview
          rationale={
            plan?.rationale ??
            "Review the proposed plan below. Approve to begin execution."
          }
          steps={
            plan?.steps ??
            workflow.steps.map((s) => ({
              position: s.position,
              tool_name: s.tool_name,
              description: s.description,
              arguments: s.arguments,
            }))
          }
          onApprove={handleApproveAndExecute}
          onReject={handleReject}
          pending={busy != null}
          usedMock={workflow.used_mock}
        />
      )}

      {!hasSteps && workflow.status === "draft" && (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Play className="h-5 w-5" />
            </div>
            <h3 className="text-base font-semibold">Ready to plan</h3>
            <p className="max-w-md text-sm text-muted-foreground">
              Click <strong>Generate plan</strong> to have the agent propose an
              ordered sequence of tool invocations for this goal.
            </p>
          </CardContent>
        </Card>
      )}

      {hasSteps && (
        <Tabs defaultValue="timeline" className="space-y-4">
          <TabsList>
            <TabsTrigger value="timeline">Execution timeline</TabsTrigger>
            <TabsTrigger value="report">Report</TabsTrigger>
            <TabsTrigger value="context">Context</TabsTrigger>
          </TabsList>
          <TabsContent value="timeline" className="space-y-3">
            <Card>
              <CardHeader>
                <CardTitle>Steps</CardTitle>
              </CardHeader>
              <CardContent>
                <ExecutionTimeline steps={workflow.steps} />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="report">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0">
                <CardTitle>Markdown report</CardTitle>
                {report && (
                  <Button
                    asChild
                    variant="outline"
                    size="sm"
                    className="gap-1.5"
                  >
                    <a
                      href={`data:text/markdown;charset=utf-8,${encodeURIComponent(report.markdown)}`}
                      download={`${workflow.title.replace(/\s+/g, "-").toLowerCase()}.md`}
                    >
                      <Download className="h-4 w-4" />
                      Download
                    </a>
                  </Button>
                )}
              </CardHeader>
              <CardContent>
                {report ? (
                  <MarkdownViewer markdown={report.markdown} />
                ) : (
                  <p className="text-sm text-muted-foreground">
                    The report is generated after execution completes.
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="context">
            <Card>
              <CardHeader>
                <CardTitle>Workflow context</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-sm">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Goal
                  </p>
                  <p className="mt-1 leading-relaxed">{workflow.goal}</p>
                </div>
                {workflow.context && (
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Provided context
                    </p>
                    <p className="mt-1 whitespace-pre-wrap leading-relaxed">
                      {workflow.context}
                    </p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-4 pt-2 text-xs text-muted-foreground">
                  <p>
                    <span className="font-medium text-foreground">ID</span>{" "}
                    <code className="rounded bg-muted px-1.5 py-0.5">
                      {workflow.id}
                    </code>
                  </p>
                  <p>
                    <span className="font-medium text-foreground">Mode</span>{" "}
                    {workflow.used_mock ? "Mock" : "Live"}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </>
  );
}
