"use client";

import { useEffect, useState } from "react";
import { useUser } from "@/lib/user-context";
import { api, UserSummary } from "@/lib/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ThemeToggle } from "@/components/theme-toggle";

function formatCurrency(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

export function Sidebar() {
  const { users, selectedUserId, setSelectedUserId, loading } = useUser();
  const [summary, setSummary] = useState<UserSummary | null>(null);

  useEffect(() => {
    if (!selectedUserId) return;
    setSummary(null);
    api.getSummary(selectedUserId).then(setSummary);
  }, [selectedUserId]);

  return (
    <aside className="w-72 shrink-0 border-r border-border bg-sidebar p-5 flex flex-col gap-5">
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Finance Assistant</h1>
        <p className="text-sm text-muted-foreground">RAG + anomaly detection</p>
      </div>

      <div className="space-y-2">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Viewing as
        </p>
        {loading ? (
          <Skeleton className="h-9 w-full" />
        ) : (
          <Select value={selectedUserId ?? undefined} onValueChange={setSelectedUserId}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select a user" />
            </SelectTrigger>
            <SelectContent>
              {users.map((u) => (
                <SelectItem key={u.user_id} value={u.user_id}>
                  {u.user_id} &middot; {u.transaction_count} txns
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      <div className="space-y-3">
        {!summary ? (
          <>
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </>
        ) : (
          <>
            <StatCard label="Total spend" value={formatCurrency(summary.total_spend)} />
            <StatCard label="Total income" value={formatCurrency(summary.total_income)} tone="success" />
            <StatCard
              label="Flagged transactions"
              value={String(summary.anomalies_count)}
              tone={summary.anomalies_count > 0 ? "destructive" : "default"}
            />
          </>
        )}
      </div>

      <div className="mt-auto flex items-center justify-between">
        {summary?.date_range_start && (
          <p className="text-xs text-muted-foreground tabular-nums">
            {summary.date_range_start} to {summary.date_range_end}
          </p>
        )}
        <ThemeToggle />
      </div>
    </aside>
  );
}

function StatCard({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: "default" | "success" | "destructive";
}) {
  const toneClass =
    tone === "success" ? "text-success" : tone === "destructive" ? "text-destructive" : "text-foreground";

  return (
    <Card className="shadow-none">
      <CardContent className="px-4 py-3">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className={`text-xl font-semibold tabular-nums ${toneClass}`}>{value}</p>
      </CardContent>
    </Card>
  );
}
