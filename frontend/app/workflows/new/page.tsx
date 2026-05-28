"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Loader2, Play } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { api, ApiRequestError } from "@/lib/api";

const TEMPLATES: { title: string; goal: string }[] = [
  {
    title: "Research agent observability patterns",
    goal: "Compile a short briefing on best practices for observing agent workflows in production, including timing data, tool-level logs, and reporting patterns.",
  },
  {
    title: "Plan Postgres 16 migration",
    goal: "Generate a step-by-step migration plan for moving a production service from Postgres 13 to Postgres 16 with minimal downtime.",
  },
  {
    title: "Draft an incident retro",
    goal: "Summarize the events of yesterday's checkout outage and propose three concrete follow-up actions.",
  },
];

export default function NewWorkflowPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("");
  const [context, setContext] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [planning, setPlanning] = useState(false);

  const submit = async (planNow: boolean) => {
    if (title.trim().length < 3) {
      toast.error("Add a short title (3 characters or more).");
      return;
    }
    if (goal.trim().length < 10) {
      toast.error("Describe your goal in at least 10 characters.");
      return;
    }

    try {
      setSubmitting(true);
      const workflow = await api.createWorkflow({
        title: title.trim(),
        goal: goal.trim(),
        context: context.trim() || undefined,
      });
      toast.success("Workflow created.");

      if (planNow) {
        setPlanning(true);
        await api.planWorkflow(workflow.id);
        toast.success("Plan generated — review and approve to execute.");
      }
      router.push(`/workflows/${workflow.id}`);
    } catch (e) {
      const message =
        e instanceof ApiRequestError ? e.message : (e as Error).message;
      toast.error(message);
    } finally {
      setSubmitting(false);
      setPlanning(false);
    }
  };

  return (
    <>
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">
          New workflow
        </h1>
        <p className="text-sm text-muted-foreground">
          Describe what you want done — the planner will propose a step-by-step
          plan using the registered tool catalog. No tools execute until you
          approve.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Workflow goal</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="space-y-2">
              <label
                htmlFor="title"
                className="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
              >
                Title
              </label>
              <Input
                id="title"
                placeholder="e.g. Research agent observability patterns"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={200}
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="goal"
                className="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
              >
                Goal
              </label>
              <Textarea
                id="goal"
                placeholder="What should the agent accomplish?"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                maxLength={4000}
                rows={6}
              />
              <p className="text-xs text-muted-foreground">
                Be specific — describe the inputs, the desired output, and any
                constraints.
              </p>
            </div>
            <div className="space-y-2">
              <label
                htmlFor="context"
                className="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
              >
                Additional context <span className="font-normal text-muted-foreground/70">(optional)</span>
              </label>
              <Textarea
                id="context"
                placeholder="Background information the agent should know."
                value={context}
                onChange={(e) => setContext(e.target.value)}
                maxLength={4000}
                rows={3}
              />
            </div>
            <div className="flex flex-wrap items-center justify-end gap-2 border-t pt-4">
              <Button
                variant="outline"
                onClick={() => submit(false)}
                disabled={submitting}
              >
                Save as draft
              </Button>
              <Button onClick={() => submit(true)} disabled={submitting}>
                {planning ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Planning…
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Create & plan
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Start from a template</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {TEMPLATES.map((t) => (
              <button
                key={t.title}
                type="button"
                onClick={() => {
                  setTitle(t.title);
                  setGoal(t.goal);
                }}
                className="w-full rounded-lg border bg-background p-3 text-left text-sm transition-colors hover:border-primary/50 hover:bg-primary/5"
              >
                <p className="font-medium">{t.title}</p>
                <p className="mt-1 text-xs text-muted-foreground">{t.goal}</p>
              </button>
            ))}
            <p className="rounded-lg bg-muted/40 p-3 text-xs leading-relaxed text-muted-foreground">
              Templates are local presets — clicking one fills the form. You can
              edit anything before submitting.
            </p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
