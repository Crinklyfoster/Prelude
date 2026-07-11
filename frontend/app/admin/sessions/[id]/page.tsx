"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getSession, type AdminMessage } from "@/lib/admin";

export default function SessionDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: messages = [], isLoading, isError } = useQuery({
    queryKey: ["admin-session", id],
    queryFn: () => getSession(id),
    enabled: !!id,
  });

  return (
    <div className="max-w-3xl">
      {/* Back link */}
      <Link
        href="/admin/sessions"
        className="inline-flex items-center gap-1.5 mb-6 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        ← Back to Sessions
      </Link>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Conversation Viewer
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Full message thread for session{" "}
          <code className="rounded bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 text-xs font-mono">
            {id}
          </code>
        </p>
      </div>

      {/* Loading skeletons */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={`skel-msg-${i}`}
              className={`flex ${i % 2 === 0 ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`h-16 rounded-2xl animate-pulse ${
                  i % 2 === 0
                    ? "w-2/3 bg-blue-100 dark:bg-blue-900/30"
                    : "w-3/4 bg-gray-100 dark:bg-gray-800"
                }`}
              />
            </div>
          ))}
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/30 p-4 text-sm text-red-700 dark:text-red-400">
          Failed to load session messages.
        </div>
      )}

      {/* Empty */}
      {!isLoading && !isError && messages.length === 0 && (
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-12 text-center text-gray-400 dark:text-gray-600">
          This session has no messages yet.
        </div>
      )}

      {/* Conversation thread */}
      {!isLoading && messages.length > 0 && (
        <div className="space-y-4">
          {messages.map((msg: AdminMessage) => {
            const isUser = msg.role === "user";

            return (
              <div
                key={msg.id}
                className={`flex ${isUser ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[75%] rounded-2xl px-5 py-3.5 shadow-sm ${
                    isUser
                      ? "rounded-br-sm bg-blue-600 text-white"
                      : "rounded-bl-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white"
                  }`}
                >
                  {/* Role label */}
                  <p
                    className={`mb-1.5 text-xs font-semibold uppercase tracking-wide ${
                      isUser
                        ? "text-blue-200"
                        : "text-gray-400 dark:text-gray-500"
                    }`}
                  >
                    {isUser ? "User" : "Assistant"}
                  </p>

                  {/* Message body */}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </p>

                  {/* Timestamp */}
                  <p
                    className={`mt-2 text-xs ${
                      isUser ? "text-blue-300" : "text-gray-400 dark:text-gray-600"
                    }`}
                  >
                    {new Date(msg.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Message count footer */}
      {!isLoading && messages.length > 0 && (
        <p className="mt-8 text-center text-xs text-gray-400 dark:text-gray-600">
          {messages.length} message{messages.length !== 1 ? "s" : ""} in this session
        </p>
      )}
    </div>
  );
}
