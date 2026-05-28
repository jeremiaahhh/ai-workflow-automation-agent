"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ListChecks,
  PlusCircle,
  Wrench,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/workflows", label: "Workflows", icon: ListChecks },
  { href: "/workflows/new", label: "New workflow", icon: PlusCircle },
  { href: "/tools", label: "Tool catalog", icon: Wrench },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 border-r bg-card/50 backdrop-blur-sm lg:flex lg:flex-col">
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-indigo-500 text-primary-foreground shadow-lg">
          <Sparkles className="h-4 w-4" />
        </div>
        <div className="leading-tight">
          <p className="text-sm font-semibold tracking-tight">Forge Agent</p>
          <p className="text-[11px] uppercase tracking-wider text-muted-foreground">
            AI Workflow Studio
          </p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-4 text-xs text-muted-foreground">
        <p className="font-medium text-foreground">Plan → Approve → Execute</p>
        <p className="mt-1 leading-relaxed">
          Every workflow runs through a human checkpoint before tools execute.
        </p>
      </div>
    </aside>
  );
}
