"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface Settings {
  version: string;
  chat_model: string;
  embedding_model: string;
  retrieval_mode: string;
  top_k: number;
  chunk_size: number;
  chunk_overlap: number;
  query_rewrite: boolean;
  reranker: boolean;
  jwt_algorithm: string;
  jwt_expire_minutes: number;
  providers: {
    ollama: boolean;
    gemini: boolean;
    groq: boolean;
  };
}

function Card({
  title,
  children,
}: Readonly<{
  title: string;
  children: React.ReactNode;
}>) {
  return (
    <div className="rounded-xl border bg-white dark:bg-gray-800 p-6 shadow-sm">
      <h2 className="mb-4 font-semibold text-lg">{title}</h2>
      {children}
    </div>
  );
}

export default function SettingsPage() {
  const { data } = useQuery<Settings>({
    queryKey: ["admin-settings"],
    queryFn: async () => {
      const res = await api.get("/admin/settings");
      return res.data;
    },
  });

  if (!data) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">System Settings</h1>

      <Card title="🤖 AI Configuration">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="chat_model" className="text-sm font-medium">Chat Model</label>
            <select
              id="chat_model"
              disabled
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
              value={data.chat_model}
            >
              <option>{data.chat_model}</option>
            </select>
          </div>

          <div>
            <label htmlFor="embedding_model" className="text-sm font-medium">Embedding Model</label>
            <select
              id="embedding_model"
              disabled
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
              value={data.embedding_model}
            >
              <option>{data.embedding_model}</option>
            </select>
          </div>

          <div>
            <label htmlFor="retrieval_mode" className="text-sm font-medium">Retrieval Mode</label>
            <select
              id="retrieval_mode"
              disabled
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
              value={data.retrieval_mode}
            >
              <option>{data.retrieval_mode}</option>
            </select>
          </div>

          <div>
            <label htmlFor="top_k" className="text-sm font-medium">Top K</label>
            <input
              id="top_k"
              disabled
              value={data.top_k}
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
            />
          </div>

          <div>
            <label htmlFor="chunk_size" className="text-sm font-medium">Chunk Size</label>
            <input
              id="chunk_size"
              disabled
              value={data.chunk_size}
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
            />
          </div>

          <div>
            <label htmlFor="chunk_overlap" className="text-sm font-medium">Chunk Overlap</label>
            <input
              id="chunk_overlap"
              disabled
              value={data.chunk_overlap}
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={data.query_rewrite}
              disabled
            />
            <span>Query Rewrite</span>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={data.reranker}
              disabled
            />
            <span>Reranker</span>
          </div>
        </div>
      </Card>

      <Card title="☁ Providers">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-xl border p-5">
            <h3 className="font-semibold">Ollama</h3>
            <p className={data.providers.ollama ? "mt-2 text-emerald-500" : "mt-2 text-gray-400"}>
              {data.providers.ollama ? "● Connected" : "○ Not Configured"}
            </p>
            <p className="text-sm text-muted-foreground">
              Local CPU Inference
            </p>
          </div>

          <div className="rounded-xl border p-5">
            <h3 className="font-semibold">Gemini</h3>
            <p className={data.providers.gemini ? "mt-2 text-emerald-500" : "mt-2 text-gray-400"}>
              {data.providers.gemini ? "● Connected" : "○ Not Configured"}
            </p>
            <p className="text-sm text-muted-foreground">
              API Key Required
            </p>
          </div>

          <div className="rounded-xl border p-5">
            <h3 className="font-semibold">Groq</h3>
            <p className={data.providers.groq ? "mt-2 text-emerald-500" : "mt-2 text-gray-400"}>
              {data.providers.groq ? "● Connected" : "○ Not Configured"}
            </p>
            <p className="text-sm text-muted-foreground">
              API Key Required
            </p>
          </div>
        </div>
      </Card>

      <Card title="🛡 Security">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label htmlFor="jwt_algorithm" className="text-sm font-medium">
              JWT Algorithm
            </label>
            <input
              id="jwt_algorithm"
              disabled
              value={data.jwt_algorithm}
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
            />
          </div>
          <div>
            <label htmlFor="jwt_expire_minutes" className="text-sm font-medium">
              Access Token
            </label>
            <input
              id="jwt_expire_minutes"
              disabled
              value={`${data.jwt_expire_minutes} minutes`}
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
            />
          </div>
          <div>
            <label htmlFor="version" className="text-sm font-medium">
              Version
            </label>
            <input
              id="version"
              disabled
              value={data.version}
              className="mt-2 w-full rounded-lg border p-3 bg-muted"
            />
          </div>
        </div>
      </Card>

      <Card title="🔧 Maintenance">
        <div className="grid grid-cols-2 gap-4">
          <Button disabled>
            Reindex Documents
          </Button>
          <Button disabled>
            Restart Ollama
          </Button>
          <Button disabled>
            Clear Cache
          </Button>
          <Button disabled>
            Export Logs
          </Button>
        </div>
      </Card>

      <Card title="📊 Monitoring">
        <div className="flex flex-wrap gap-3">
          <a
            href="http://localhost:3001"
            target="_blank"
            rel="noreferrer"
            className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
          >
            Grafana
          </a>
          <a
            href="http://localhost:9090"
            target="_blank"
            rel="noreferrer"
            className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
          >
            Prometheus
          </a>
          <a
            href="http://localhost:8080"
            target="_blank"
            rel="noreferrer"
            className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
          >
            cAdvisor
          </a>
        </div>
      </Card>

    </div>
  );
}
