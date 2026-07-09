"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function LogsPage() {
  const { data: status, isLoading } = useQuery({
    queryKey: ["admin-logs-status"],
    queryFn: async () => {
      const res = await api.get<{ message: string }>("/admin/logs");
      return res.data;
    },
  });

  const GRAFANA_URL =
    typeof window !== "undefined"
      ? `${window.location.protocol}//${window.location.hostname}/grafana/explore`
      : "/grafana/explore";

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Centralized Logs
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Query structured event logs across all backend services via Loki.
        </p>
      </div>

      {/* Info Panel */}
      <div className="rounded-xl border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 p-6 flex items-start gap-4">
        <span className="text-xl">📊</span>
        <div>
          <h2 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
            Structured Logging Enabled
          </h2>
          <p className="mt-1 text-sm text-blue-700 dark:text-blue-300">
            {isLoading ? "Checking log service..." : (status?.message || "Logs are actively being collected.")}
          </p>
          <div className="mt-4 flex gap-3">
            <a
              href={GRAFANA_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              Open Grafana Explore ↗
            </a>
          </div>
        </div>
      </div>

      {/* Quick Queries (Mock layout for future expansion) */}
      <section>
        <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-4">
          Quick Queries
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Search Recent Errors</h3>
            <code className="block w-full bg-gray-50 dark:bg-gray-900 rounded p-3 text-xs text-red-600 dark:text-red-400 font-mono break-all">
              {`{job="docker"} | json | level="ERROR"`}
            </code>
          </div>
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Filter by Document Uploads</h3>
            <code className="block w-full bg-gray-50 dark:bg-gray-900 rounded p-3 text-xs text-emerald-600 dark:text-emerald-400 font-mono break-all">
              {`{job="docker"} | json | event_type="document" | action="upload"`}
            </code>
          </div>
        </div>
      </section>

    </div>
  );
}
