import { cn } from "@/lib/utils";
import { stepStatusVisual, workflowStatusVisual } from "@/lib/status";
import type { ExecutionStepStatus, WorkflowStatus } from "@/lib/types";

interface Props {
  status: WorkflowStatus | ExecutionStepStatus;
  variant?: "workflow" | "step";
  className?: string;
}

export function StatusBadge({ status, variant = "workflow", className }: Props) {
  const visual =
    variant === "workflow"
      ? workflowStatusVisual(status as WorkflowStatus)
      : stepStatusVisual(status as ExecutionStepStatus);
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium",
        visual.className,
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", visual.dotClass)} />
      {visual.label}
    </span>
  );
}
