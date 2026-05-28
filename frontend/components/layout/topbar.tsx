"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Moon, Sun, Activity, CircuitBoard } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export function Topbar() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [health, setHealth] = useState<{
    ok: boolean;
    mock: boolean;
  } | null>(null);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      try {
        const h = await api.health();
        if (!cancelled) setHealth({ ok: true, mock: h.mock_mode });
      } catch {
        if (!cancelled) setHealth({ ok: false, mock: true });
      }
    };
    poll();
    const id = setInterval(poll, 15_000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-4 border-b bg-background/80 px-6 backdrop-blur">
      <div className="flex items-center gap-3">
        <Link href="/" className="lg:hidden">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-indigo-500 text-primary-foreground shadow">
            <CircuitBoard className="h-4 w-4" />
          </div>
        </Link>
        <div className="hidden text-xs text-muted-foreground sm:flex sm:items-center sm:gap-1.5">
          <Activity className="h-3.5 w-3.5" />
          <span>Backend</span>
          <span
            className={cn(
              "inline-flex h-2 w-2 rounded-full",
              health?.ok ? "bg-emerald-500 animate-pulse" : "bg-rose-500",
            )}
          />
          <span className="text-foreground">
            {health == null
              ? "checking…"
              : health.ok
                ? "online"
                : "offline"}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {health?.mock !== undefined && (
          <span
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium",
              health.mock
                ? "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200"
                : "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200",
            )}
          >
            <span
              className={cn(
                "h-1.5 w-1.5 rounded-full",
                health.mock ? "bg-amber-500" : "bg-emerald-500",
              )}
            />
            {health.mock ? "Mock mode" : "Live AI"}
          </span>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          aria-label="Toggle theme"
        >
          {mounted && theme === "dark" ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>
      </div>
    </header>
  );
}
