import type { ExecutionStepStatus, WorkflowStatus } from "./types";

interface StatusVisual {
  label: string;
  className: string;
  dotClass: string;
}

const WORKFLOW: Record<WorkflowStatus, StatusVisual> = {
  draft: {
    label: "Draft",
    className: "border-zinc-200 bg-zinc-100 text-zinc-700 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
    dotClass: "bg-zinc-400",
  },
  planned: {
    label: "Planned",
    className: "border-indigo-200 bg-indigo-50 text-indigo-700 dark:border-indigo-900 dark:bg-indigo-950 dark:text-indigo-200",
    dotClass: "bg-indigo-500",
  },
  approved: {
    label: "Approved",
    className: "border-sky-200 bg-sky-50 text-sky-700 dark:border-sky-900 dark:bg-sky-950 dark:text-sky-200",
    dotClass: "bg-sky-500",
  },
  running: {
    label: "Running",
    className: "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200",
    dotClass: "bg-amber-500 animate-pulse",
  },
  completed: {
    label: "Completed",
    className: "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200",
    dotClass: "bg-emerald-500",
  },
  failed: {
    label: "Failed",
    className: "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200",
    dotClass: "bg-rose-500",
  },
  rejected: {
    label: "Rejected",
    className: "border-zinc-200 bg-zinc-50 text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400",
    dotClass: "bg-zinc-500",
  },
};

const STEP: Record<ExecutionStepStatus, StatusVisual> = {
  pending: {
    label: "Pending",
    className: "border-zinc-200 bg-zinc-50 text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300",
    dotClass: "bg-zinc-400",
  },
  running: {
    label: "Running",
    className: "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200",
    dotClass: "bg-amber-500 animate-pulse",
  },
  succeeded: {
    label: "Succeeded",
    className: "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200",
    dotClass: "bg-emerald-500",
  },
  failed: {
    label: "Failed",
    className: "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200",
    dotClass: "bg-rose-500",
  },
  skipped: {
    label: "Skipped",
    className: "border-zinc-200 bg-zinc-50 text-zinc-500 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400",
    dotClass: "bg-zinc-400",
  },
};

export function workflowStatusVisual(status: WorkflowStatus): StatusVisual {
  return WORKFLOW[status];
}

export function stepStatusVisual(status: ExecutionStepStatus): StatusVisual {
  return STEP[status];
}
