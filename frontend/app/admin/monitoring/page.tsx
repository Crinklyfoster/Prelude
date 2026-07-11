"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface SystemStatus {
  backend: string;
  database: string;
  chroma: string;
  ollama: string;
  retrieval_mode: string;
  llm: string;
  version: string;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function healthColor(value: string) {
  if (value === "healthy") return "text-emerald-600 dark:text-emerald-400";
  if (value === "degraded") return "text-amber-600 dark:text-amber-400";
  return "text-red-600 dark:text-red-400";
}

function healthDot(value: string) {
  if (value === "healthy") return "bg-emerald-500";
  if (value === "degraded") return "bg-amber-500";
  return "bg-red-500";
}

function HealthCard({
  label,
  value,
}: Readonly<{
  label: string;
  value: string;
}>) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm flex items-center gap-4">
      <span
        className={`shrink-0 w-3 h-3 rounded-full animate-pulse ${healthDot(value)}`}
      />
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          {label}
        </p>
        <p className={`mt-0.5 text-lg font-bold capitalize ${healthColor(value)}`}>
          {value}
        </p>
      </div>
    </div>
  );
}

function InfoCard({ label, value }: Readonly<{ label: string; value: string }>) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
        {label}
      </p>
      <p className="mt-0.5 text-lg font-bold text-gray-900 dark:text-white font-mono">
        {value}
      </p>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function MonitoringPage() {
  const { data: sys, isLoading } = useQuery<SystemStatus>({
    queryKey: ["admin-system"],
    queryFn: async () => {
      const res = await api.get<SystemStatus>("/admin/system");
      return res.data;
    },
    refetchInterval: 30_000,
  });

  const GRAFANA_URL =
    process.env.NEXT_PUBLIC_GRAFANA_URL ?? "http://localhost:3001";
  const PROMETHEUS_URL =
    process.env.NEXT_PUBLIC_PROMETHEUS_URL ?? "http://localhost:9090";
  const METRICS_URL =
    process.env.NEXT_PUBLIC_METRICS_URL ?? "http://localhost/api/metrics";

  return (
    <div className="space-y-10">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Monitoring
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Real-time system health and observability.
        </p>
      </div>

      {/* ── Health Cards ───────────────────────────────────────── */}
      <section>
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
          Service Health
        </h2>

        {isLoading && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={`skel-card-${i}`}
                className="h-20 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 animate-pulse"
              />
            ))}
          </div>
        )}
        {!isLoading && sys && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <HealthCard label="Backend" value={sys.backend} />
            <HealthCard label="Database" value={sys.database} />
            <HealthCard label="Chroma" value={sys.chroma} />
            <HealthCard label="Ollama / LLM" value={sys.ollama} />
          </div>
        )}
      </section>

      {/* ── Config Info ────────────────────────────────────────── */}
      {sys && (
        <section>
          <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
            Configuration
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <InfoCard label="LLM Model" value={sys.llm} />
            <InfoCard label="Retrieval Mode" value={sys.retrieval_mode} />
            <InfoCard label="Version" value={sys.version} />
          </div>
        </section>
      )}

      {/* ── Grafana Link ──────────────────────────────────────── */}
      <section>
        <div className="rounded-xl border p-6 bg-white dark:bg-gray-800">
          <h3 className="font-semibold text-lg">
            Grafana Dashboard
          </h3>

          <p className="mt-2 text-sm text-gray-500">
            Open the Enterprise monitoring dashboard in Grafana.
          </p>

          <a
            href={GRAFANA_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-flex rounded-lg bg-blue-600 px-4 py-2 text-white"
          >
            Open Grafana →
          </a>
        </div>
      </section>

      {/* ── Quick Links ────────────────────────────────────────── */}
      <section>
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
          Quick Links
        </h2>
        <div className="flex flex-wrap gap-3">
          {[
            { label: "📊 Grafana", href: GRAFANA_URL },
            { label: "🔎 Prometheus", href: PROMETHEUS_URL },
            { label: "📈 Backend Metrics", href: METRICS_URL },
          ].map(({ label, href }) => (
            <a
              key={href}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm"
            >
              {label}
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}
