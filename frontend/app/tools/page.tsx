"use client";

import { useEffect, useState } from "react";
import { Wrench } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { ToolDefinition } from "@/lib/types";

export default function ToolsPage() {
  const [tools, setTools] = useState<ToolDefinition[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.tools().then(setTools).catch((e: Error) => setError(e.message));
  }, []);

  return (
    <>
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Tool catalog</h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          These are the only tools the agent can invoke. Each tool has a typed
          input schema and runs locally with no network access — that’s the
          safety boundary that makes the plan-then-execute loop trustworthy.
        </p>
      </header>

      {error ? (
        <p className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
          Couldn’t load tools: {error}
        </p>
      ) : tools == null ? (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {tools.map((tool) => (
            <Card key={tool.name}>
              <CardHeader className="flex flex-row items-start gap-3 space-y-0">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Wrench className="h-4 w-4" />
                </div>
                <div className="space-y-1">
                  <CardTitle className="text-base">
                    <code className="rounded bg-muted px-1.5 py-0.5 text-sm">
                      {tool.name}
                    </code>
                  </CardTitle>
                  <CardDescription>{tool.description}</CardDescription>
                </div>
              </CardHeader>
              <CardContent>
                <details>
                  <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                    Show JSON schema
                  </summary>
                  <pre className="mt-2 max-h-72 overflow-auto rounded-lg border bg-muted/40 p-3 text-[11px] leading-relaxed">
                    {JSON.stringify(tool.input_schema, null, 2)}
                  </pre>
                </details>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
