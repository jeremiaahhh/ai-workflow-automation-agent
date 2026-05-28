import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  hint?: string;
  tone?: "default" | "primary" | "success" | "warning" | "danger";
}

const TONE: Record<NonNullable<StatCardProps["tone"]>, string> = {
  default:
    "from-zinc-500/10 to-zinc-500/0 text-zinc-600 dark:text-zinc-300",
  primary:
    "from-primary/15 to-primary/0 text-primary",
  success:
    "from-emerald-500/15 to-emerald-500/0 text-emerald-600 dark:text-emerald-300",
  warning:
    "from-amber-500/20 to-amber-500/0 text-amber-700 dark:text-amber-300",
  danger:
    "from-rose-500/15 to-rose-500/0 text-rose-600 dark:text-rose-300",
};

export function StatCard({
  label,
  value,
  icon: Icon,
  hint,
  tone = "default",
}: StatCardProps) {
  return (
    <Card className="relative overflow-hidden p-5">
      <div
        className={cn(
          "absolute inset-0 bg-gradient-to-br opacity-100 pointer-events-none",
          TONE[tone],
        )}
      />
      <div className="relative flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            {label}
          </p>
          <p className="text-3xl font-semibold tracking-tight">{value}</p>
          {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
        </div>
        <div
          className={cn(
            "flex h-10 w-10 items-center justify-center rounded-lg bg-background/80 shadow-sm ring-1 ring-border",
            TONE[tone].split(" ").filter((c) => c.startsWith("text-")).join(" "),
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </Card>
  );
}
