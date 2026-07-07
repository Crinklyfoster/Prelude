"use client";

import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth-provider";

export function AppHeader() {
  const router = useRouter();

  const { user, logout } = useAuth();

  async function handleLogout() {
    logout();
    router.replace("/login");
  }

  return (
    <header className="flex items-center justify-between border-b bg-white px-6 py-4">
      <h1 className="text-xl font-bold">Enterprise RAG</h1>

      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="font-medium">{user?.name}</p>

          <p className="text-sm text-gray-500">{user?.email}</p>
        </div>

        <button
          onClick={handleLogout}
          className="rounded-md bg-red-600 px-4 py-2 text-white hover:bg-red-700"
        >
          Logout
        </button>
      </div>
    </header>
  );
}

