"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useUser } from "@/lib/user-context";
import { api, AnomalyRow, CategorySpend } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ChartColumn, TriangleAlert } from "lucide-react";

function formatCurrency(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: { payload: CategorySpend }[] }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-md border border-border bg-popover px-3 py-2 text-sm shadow-sm">
      <p className="font-medium text-popover-foreground">{row.category}</p>
      <p className="text-muted-foreground tabular-nums">{formatCurrency(row.total)}</p>
    </div>
  );
}

export function Dashboard() {
  const { selectedUserId } = useUser();
  const [categories, setCategories] = useState<CategorySpend[] | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyRow[] | null>(null);

  useEffect(() => {
    if (!selectedUserId) return;
    setCategories(null);
    setAnomalies(null);
    api.getSpendByCategory(selectedUserId).then(setCategories);
    api.getAnomalies(selectedUserId).then(setAnomalies);
  }, [selectedUserId]);

  return (
    <div className="flex flex-col gap-6 p-6 max-w-5xl mx-auto w-full">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChartColumn className="h-4 w-4 text-muted-foreground" /> Spend by category
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!categories ? (
            <Skeleton className="h-64 w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={categories} margin={{ left: 8, right: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis
                  dataKey="category"
                  tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                  axisLine={{ stroke: "var(--border)" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                  width={52}
                  tickFormatter={(v: number) =>
                    v >= 1000 ? `${Math.round(v / 1000)}k` : String(v)
                  }
                />
                <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--muted)" }} />
                <Bar dataKey="total" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TriangleAlert className="h-4 w-4 text-destructive" /> Flagged transactions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!anomalies ? (
            <Skeleton className="h-40 w-full" />
          ) : anomalies.length === 0 ? (
            <p className="text-sm text-muted-foreground">No flagged transactions for this user.</p>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead className="text-right">Typical range</TableHead>
                    <TableHead>Note</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {anomalies.map((row) => (
                    <TableRow key={row.transaction_id_clean}>
                      <TableCell className="tabular-nums">{row.date_clean}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{row.category_clean}</Badge>
                      </TableCell>
                      <TableCell className="text-right tabular-nums text-destructive font-medium">
                        {formatCurrency(row.amount_clean)}
                      </TableCell>
                      <TableCell className="text-right tabular-nums text-muted-foreground text-xs">
                        {formatCurrency(row.lower_bound)} - {formatCurrency(row.upper_bound)}
                      </TableCell>
                      <TableCell className="text-muted-foreground text-xs max-w-48 truncate">
                        {row.notes || "-"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
