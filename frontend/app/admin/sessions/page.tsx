"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getSessions,
  deleteSession,
  type AdminSession,
} from "@/lib/admin";

export default function SessionsPage() {
  const queryClient = useQueryClient();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: sessions = [], isLoading } = useQuery({
    queryKey: ["admin-sessions"],
    queryFn: getSessions,
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteSession(id),
    onSuccess: () => {
      setErrorMsg(null);
      queryClient.invalidateQueries({ queryKey: ["admin-sessions"] });
      queryClient.invalidateQueries({ queryKey: ["admin-dashboard"] });
    },
    onError: (e: { response?: { data?: { detail?: string } } }) => {
      setErrorMsg(e?.response?.data?.detail ?? "Failed to delete session");
    },
  });

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Session Management
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Inspect and manage all chat sessions across the platform.
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
              {["Title", "Owner", "Created", "Messages", "Actions"].map((h) => (
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
            {/* Skeletons */}
            {isLoading &&
              [1, 2, 3, 4, 5, 6].map((i) => (
                <tr key={`skel-row-${i}`}>
                  {[1, 2, 3, 4, 5].map((j) => (
                    <td key={`skel-col-${j}`} className="px-6 py-4">
                      <div className="h-4 rounded bg-gray-100 dark:bg-gray-700 animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))}

            {/* Empty state */}
            {!isLoading && sessions.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="px-6 py-10 text-center text-gray-400 dark:text-gray-600"
                >
                  No sessions found.
                </td>
              </tr>
            )}

            {/* Data rows */}
            {sessions.map((s: AdminSession) => (
              <tr
                key={s.id}
                className="hover:bg-gray-50 dark:hover:bg-gray-700/40 transition-colors"
              >
                {/* Title */}
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white max-w-xs truncate">
                  {s.title}
                </td>

                {/* Owner */}
                <td className="px-6 py-4 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {s.owner}
                </td>

                {/* Created */}
                <td className="px-6 py-4 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {new Date(s.created_at).toLocaleDateString()}
                </td>

                {/* Message count */}
                <td className="px-6 py-4">
                  <span className="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2.5 py-0.5 text-xs font-semibold text-gray-700 dark:text-gray-300">
                    {s.message_count}
                  </span>
                </td>

                {/* Actions */}
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/admin/sessions/${s.id}`}
                      className="rounded-md px-3 py-1.5 text-xs font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
                    >
                      👁 View
                    </Link>

                    <button
                      disabled={remove.isPending}
                      onClick={() => {
                        if (
                          window.confirm(
                            `Delete session "${s.title}"? All messages will be permanently removed.`
                          )
                        ) {
                          remove.mutate(s.id);
                        }
                      }}
                      className="rounded-md px-3 py-1.5 text-xs font-semibold bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/60 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      🗑 Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Footer count */}
        {!isLoading && sessions.length > 0 && (
          <div className="border-t border-gray-100 dark:border-gray-700 px-6 py-3 text-xs text-gray-400 dark:text-gray-600">
            {sessions.length} session{sessions.length !== 1 ? "s" : ""} total
          </div>
        )}
      </div>
    </div>
  );
}
