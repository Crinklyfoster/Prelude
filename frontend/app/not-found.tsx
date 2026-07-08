import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="text-5xl font-bold">404</h1>

      <p className="mt-3 text-gray-500">Page not found.</p>

      <Link
        href="/chat"
        className="mt-6 rounded bg-blue-600 px-4 py-2 text-white"
      >
        Back to Chat
      </Link>
    </main>
  );
}

