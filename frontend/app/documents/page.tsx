"use client";

import DocumentList from "@/components/documents/DocumentList";
import DocumentUpload from "@/components/documents/DocumentUpload";
import { useDocuments } from "@/hooks/useDocuments";
import { AuthGuard } from "@/components/auth/AuthGuard";

export default function DocumentsPage() {
  const { data, isLoading, isError, isFetching, refetch } =
    useDocuments();

  return (
    <AuthGuard>
      <main className="p-8">
        <h1 className="text-3xl font-bold">Documents</h1>

        <div className="mt-6">
          <DocumentUpload />

          {isLoading && (
            <div
              className="mt-6 space-y-4"
              aria-label="Loading documents"
              aria-busy="true"
            >
              {[1, 2, 3].map((item) => (
                <div
                  key={item}
                  className="h-28 animate-pulse rounded-lg bg-muted"
                />
              ))}
            </div>
          )}

          {isError && (
            <div className="py-12 text-center">
              <p className="font-medium">
                Failed to load documents.
              </p>

              <button
                type="button"
                onClick={() => void refetch()}
                disabled={isFetching}
                className="mt-4 rounded border border-gray-300 px-4 py-2 hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700"
              >
                {isFetching ? "Retrying..." : "Retry"}
              </button>
            </div>
          )}

          {!isLoading && !isError && (
            <DocumentList documents={data ?? []} />
          )}
        </div>
      </main>
    </AuthGuard>
  );
}

