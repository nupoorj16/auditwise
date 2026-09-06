"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/user-context";
import { api, UserSummary } from "@/lib/api";
import { getPersona } from "@/lib/identity";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AccountSwitcher } from "@/components/account-switcher";
import { ThemeToggle } from "@/components/theme-toggle";
import { BookCheck, Wallet, TrendingUp, TriangleAlert } from "lucide-react";

function formatCurrency(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

export function Sidebar() {
  const { selectedUserId } = useUser();
  const [summary, setSummary] = useState<UserSummary | null>(null);

  useEffect(() => {
    if (!selectedUserId) return;
    setSummary(null);
    api.getSummary(selectedUserId).then(setSummary);
  }, [selectedUserId]);

  return (
    <aside className="w-72 shrink-0 border-r border-border bg-sidebar p-5 flex flex-col gap-6">
      <div className="flex items-center gap-2.5">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
          <BookCheck className="h-5 w-5" strokeWidth={2.25} />
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-tight leading-none">AuditWise</h1>
          <p className="text-xs text-muted-foreground mt-1">Finance RAG + anomaly detection</p>
        </div>
      </div>

      <div className="flex flex-col gap-2.5">
        <AccountSwitcher />
        <p className="text-xs text-muted-foreground leading-relaxed px-0.5">
          {getPersona(selectedUserId).backstory}
        </p>
      </div>

      <div className="space-y-2.5">
        {!summary ? (
          <>
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </>
        ) : (
          <>
            <StatCard icon={Wallet} label="Total spend" value={formatCurrency(summary.total_spend)} />
            <StatCard icon={TrendingUp} label="Total income" value={formatCurrency(summary.total_income)} tone="success" />
            <StatCard
              icon={TriangleAlert}
              label="Flagged transactions"
              value={String(summary.anomalies_count)}
              tone={summary.anomalies_count > 0 ? "destructive" : "default"}
            />
          </>
        )}
      </div>

      <div className="mt-auto flex items-center justify-between gap-2">
        {summary?.date_range_start && (
          <p className="text-xs text-muted-foreground tabular-nums truncate">
            {summary.date_range_start} to {summary.date_range_end}
          </p>
        )}
        <ThemeToggle />
      </div>
    </aside>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  tone = "default",
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  tone?: "default" | "success" | "destructive";
}) {
  const toneClass =
    tone === "success" ? "text-success" : tone === "destructive" ? "text-destructive" : "text-foreground";
  const iconBg =
    tone === "success" ? "bg-success/10 text-success" : tone === "destructive" ? "bg-destructive/10 text-destructive" : "bg-accent text-accent-foreground";

  return (
    <Card className="shadow-sm border-border/80">
      <CardContent className="px-4 py-3 flex items-center gap-3">
        <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${iconBg}`}>
          <Icon className="h-4.5 w-4.5" />
        </div>
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground truncate">{label}</p>
          <p className={`text-lg font-semibold tabular-nums leading-tight ${toneClass}`}>{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}
