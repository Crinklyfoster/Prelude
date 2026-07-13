"use client";

import { useAuth } from "@/lib/auth-provider";

export default function Topbar() {
  const { user } = useAuth();

  return (
    <header className="h-16 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex items-center justify-between px-6 sticky top-0 z-10">
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">
        Admin Dashboard
      </h2>

      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-500 dark:text-gray-400">
          Prelude
        </span>

        {user && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-100 dark:bg-blue-900/40 px-3 py-1 text-xs font-semibold text-blue-700 dark:text-blue-300">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            {user.email}
          </span>
        )}
      </div>
    </header>
  );
}
