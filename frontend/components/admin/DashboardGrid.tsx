"use client";

import { useQuery } from "@tanstack/react-query";
import { getDashboard } from "@/lib/admin";
import StatCard from "@/components/admin/StatCard";

function statusAccent(value: string): "green" | "yellow" | "red" {
  if (value === "healthy") return "green";
  if (value === "degraded") return "yellow";
  return "red";
}

export default function DashboardGrid() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: getDashboard,
    refetchInterval: 30_000, // auto-refresh every 30 s
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="h-28 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 p-4 text-sm text-red-700 dark:text-red-400">
        Failed to load dashboard stats. Check that the backend is reachable and
        you are logged in as an admin.
      </div>
    );
  }

  return (
    <div className="space-y-10">
      {/* ── Usage ───────────────────────────────────────── */}
      <section>
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
          Usage
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Users" value={data.users} accent="blue" />
          <StatCard title="Documents" value={data.documents} accent="blue" />
          <StatCard title="Sessions" value={data.sessions} accent="blue" />
          <StatCard title="Messages" value={data.messages} accent="blue" />
        </div>
      </section>

      {/* ── System Health ────────────────────────────────── */}
      <section>
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
          System Health
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard
            title="Database"
            value={data.database}
            accent={statusAccent(data.database)}
          />
          <StatCard
            title="Ollama"
            value={data.ollama}
            accent={statusAccent(data.ollama)}
          />
          <StatCard
            title="Status"
            value={data.status}
            accent={statusAccent(data.status)}
          />
        </div>
      </section>
    </div>
  );
}
