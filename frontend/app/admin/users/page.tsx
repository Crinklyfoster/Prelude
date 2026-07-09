"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getUsers,
  promoteUser,
  demoteUser,
  deleteUser,
  type AdminUser,
} from "@/lib/admin";

// ── Helpers ────────────────────────────────────────────────────────────────────

function RoleBadge({ role }: { role: string }) {
  const isAdmin = role === "admin";
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
        isAdmin
          ? "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300"
          : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
      }`}
    >
      {role}
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
  variant: "promote" | "demote" | "delete";
  disabled?: boolean;
}) {
  const styles = {
    promote:
      "bg-emerald-100 text-emerald-700 hover:bg-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:hover:bg-emerald-900/60",
    demote:
      "bg-amber-100 text-amber-700 hover:bg-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:hover:bg-amber-900/60",
    delete:
      "bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/60",
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

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["admin-users"],
    queryFn: getUsers,
  });

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    queryClient.invalidateQueries({ queryKey: ["admin-dashboard"] });
  }

  const promote = useMutation({
    mutationFn: (id: string) => promoteUser(id),
    onSuccess: () => { setErrorMsg(null); invalidate(); },
    onError: (e: { response?: { data?: { detail?: string } } }) => {
      setErrorMsg(e?.response?.data?.detail ?? "Failed to promote user");
    },
  });

  const demote = useMutation({
    mutationFn: (id: string) => demoteUser(id),
    onSuccess: () => { setErrorMsg(null); invalidate(); },
    onError: (e: { response?: { data?: { detail?: string } } }) => {
      setErrorMsg(e?.response?.data?.detail ?? "Failed to demote user");
    },
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteUser(id),
    onSuccess: () => { setErrorMsg(null); invalidate(); },
    onError: (e: { response?: { data?: { detail?: string } } }) => {
      setErrorMsg(e?.response?.data?.detail ?? "Failed to delete user");
    },
  });

  const isMutating =
    promote.isPending || demote.isPending || remove.isPending;

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          User Management
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Promote, demote, or remove users from the platform.
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
              {["Name", "Email", "Role", "Joined", "Actions"].map((h) => (
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
            {isLoading &&
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  {Array.from({ length: 5 }).map((__, j) => (
                    <td key={j} className="px-6 py-4">
                      <div className="h-4 rounded bg-gray-100 dark:bg-gray-700 animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))}

            {!isLoading && users.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="px-6 py-10 text-center text-gray-400 dark:text-gray-600"
                >
                  No users found.
                </td>
              </tr>
            )}

            {users.map((user: AdminUser) => (
              <tr
                key={user.id}
                className="hover:bg-gray-50 dark:hover:bg-gray-700/40 transition-colors"
              >
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">
                  {user.name}
                </td>

                <td className="px-6 py-4 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {user.email}
                </td>

                <td className="px-6 py-4">
                  <RoleBadge role={user.role} />
                </td>

                <td className="px-6 py-4 text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {new Date(user.created_at).toLocaleDateString()}
                </td>

                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <ActionButton
                      label="Promote"
                      variant="promote"
                      disabled={isMutating || user.role === "admin"}
                      onClick={() => promote.mutate(user.id)}
                    />
                    <ActionButton
                      label="Demote"
                      variant="demote"
                      disabled={isMutating || user.role === "user"}
                      onClick={() => demote.mutate(user.id)}
                    />
                    <ActionButton
                      label="Delete"
                      variant="delete"
                      disabled={isMutating}
                      onClick={() => {
                        if (
                          window.confirm(
                            `Delete ${user.email}? This cannot be undone.`
                          )
                        ) {
                          remove.mutate(user.id);
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
        {!isLoading && users.length > 0 && (
          <div className="border-t border-gray-100 dark:border-gray-700 px-6 py-3 text-xs text-gray-400 dark:text-gray-600">
            {users.length} user{users.length !== 1 ? "s" : ""} total
          </div>
        )}
      </div>
    </div>
  );
}
