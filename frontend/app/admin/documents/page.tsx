"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getDocuments,
  deleteDocument,
  reindexDocument,
  type AdminDocument,
} from "@/lib/admin";

// ── Helpers ────────────────────────────────────────────────────────────────────

const STATUS_STYLES: Record<string, string> = {
  indexed:
    "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  processing:
    "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  uploaded:
    "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  failed:
    "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_STYLES[status] ?? "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {status}
    </span>
  );
}

function ActionButton({
  label,
  onClick,
  variant,
  disabled,
}: {
  label: string;
  onClick: () => void;
  variant: "danger" | "secondary";
  disabled?: boolean;
}) {
  const styles = {
    danger:
      "bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/60",
    secondary:
      "bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700",
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${styles[variant]}`}
    >
      {label}
    </button>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: docs = [], isLoading } = useQuery({
    queryKey: ["admin-documents"],
    queryFn: getDocuments,
  });

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ["admin-documents"] });
    queryClient.invalidateQueries({ queryKey: ["admin-dashboard"] });
  }

  function onError(e: { response?: { data?: { detail?: string } } }, fallback: string) {
    setErrorMsg(e?.response?.data?.detail ?? fallback);
  }

  const remove = useMutation({
    mutationFn: (id: string) => deleteDocument(id),
    onSuccess: () => { setErrorMsg(null); invalidate(); },
    onError: (e) => onError(e as Parameters<typeof onError>[0], "Failed to delete document"),
  });

  const reindex = useMutation({
    mutationFn: (id: string) => reindexDocument(id),
    onSuccess: () => { setErrorMsg(null); invalidate(); },
    onError: (e) => onError(e as Parameters<typeof onError>[0], "Failed to reindex document"),
  });

  const isMutating = remove.isPending || reindex.isPending;

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Document Management
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Review, delete, or re-index documents across all users.
        </p>
      </div>

      {/* Error banner */}
      {errorMsg && (
        <div className="mb-4 flex items-start gap-3 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/30 p-4 text-sm text-red-700 dark:text-red-400">
          <span className="shrink-0">⚠️</span>
          <span>{errorMsg}</span>
          <button
            className="ml-auto shrink-0 font-semibold underline"
            onClick={() => setErrorMsg(null)}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Table */}
      <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              {["Filename", "Owner", "Status", "Uploaded", "Actions"].map((h) => (
                <th
                  key={h}
                  className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {/* Skeleton rows */}
            {isLoading &&
              Array.from({ length: 6 }).map((_, i) => (
                <tr key={i}>
                  {Array.from({ length: 5 }).map((__, j) => (
                    <td key={j} className="px-6 py-4">
                      <div className="h-4 rounded bg-gray-100 dark:bg-gray-700 animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))}

            {/* Empty state */}
            {!isLoading && docs.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="px-6 py-10 text-center text-gray-400 dark:text-gray-600"
                >
                  No documents found.
                </td>
              </tr>
            )}

            {/* Data rows */}
            {docs.map((doc: AdminDocument) => (
              <tr
                key={doc.id}
                className="hover:bg-gray-50 dark:hover:bg-gray-700/40 transition-colors"
              >
                {/* Filename */}
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white max-w-xs truncate">
                  {doc.filename}
                </td>

                {/* Owner */}
                <td className="px-6 py-4 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {doc.user?.email ?? "—"}
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  <StatusBadge status={doc.status ?? "unknown"} />
                </td>

                {/* Uploaded */}
                <td className="px-6 py-4 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {doc.uploaded_at
                    ? new Date(doc.uploaded_at).toLocaleDateString()
                    : "—"}
                </td>

                {/* Actions */}
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <ActionButton
                      label="🔄 Re-index"
                      variant="secondary"
                      disabled={isMutating || doc.status === "processing"}
                      onClick={() => reindex.mutate(doc.id)}
                    />
                    <ActionButton
                      label="🗑 Delete"
                      variant="danger"
                      disabled={isMutating}
                      onClick={() => {
                        if (
                          window.confirm(
                            `Delete "${doc.filename}"? This removes the file and all embeddings permanently.`
                          )
                        ) {
                          remove.mutate(doc.id);
                        }
                      }}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Footer count */}
        {!isLoading && docs.length > 0 && (
          <div className="border-t border-gray-100 dark:border-gray-700 px-6 py-3 text-xs text-gray-400 dark:text-gray-600">
            {docs.length} document{docs.length !== 1 ? "s" : ""} total
          </div>
        )}
      </div>
    </div>
  );
}
