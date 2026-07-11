"use client";

import { useQuery } from "@tanstack/react-query";
import { getDashboard, getProviders } from "@/lib/admin";
import StatCard from "@/components/admin/StatCard";

function getStatusLabel(status: string) {
  if (status === "healthy") return "🟢 Healthy";
  if (status === "degraded") return "🟡 Degraded";
  return "🔴 Unhealthy";
}

export default function DashboardGrid() {
  const { data: dashboardData, isLoading: isDashboardLoading, isError: isDashboardError } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: getDashboard,
    refetchInterval: 30_000, // auto-refresh every 30 s
  });

  const { data: providersData, isLoading: isProvidersLoading, isError: isProvidersError } = useQuery({
    queryKey: ["admin-providers"],
    queryFn: getProviders,
    refetchInterval: 30_000,
  });

  if (isDashboardLoading || isProvidersLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={`skeleton-card-${i}`}
            className="h-28 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (isDashboardError || isProvidersError || !dashboardData || !providersData) {
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
          <StatCard title="Users" value={dashboardData.users} accent="blue" />
          <StatCard title="Documents" value={dashboardData.documents} accent="blue" />
          <StatCard title="Sessions" value={dashboardData.sessions} accent="blue" />
          <StatCard title="Messages" value={dashboardData.messages} accent="blue" />
        </div>
      </section>

      {/* ── Providers ────────────────────────────────── */}
      <section>
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
          LLM Providers
        </h2>
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Provider</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Model</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Active</th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Avg Latency</th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Requests</th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Failures</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800">
              {providersData.providers.map((p) => (
                <tr key={p.name}>
                  <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900 dark:text-white capitalize">{p.name}</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{p.model}</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {getStatusLabel(p.status)}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{p.active ? "✅" : ""}</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-right text-gray-500 dark:text-gray-400">{p.latency_ms} ms</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-right text-gray-500 dark:text-gray-400">{p.requests}</td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-right text-gray-500 dark:text-gray-400">{p.failures}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
