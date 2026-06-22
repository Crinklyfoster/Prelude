"use client";

import Link from "next/link";

import { Trash2 } from "lucide-react";

import { useDocuments } from "@/hooks/useDocuments";
import { useDeleteDocument } from "@/hooks/useDeleteDocument";

export default function LibraryPage() {
  const {
    data: documents,
    isLoading,
    isError,
  } = useDocuments();

  const deleteMutation = useDeleteDocument();

  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold">
        Library
      </h1>

      <p className="mt-2 text-muted-foreground">
        Workspace documents
      </p>

      <div className="mt-6 space-y-3">
        {isLoading && (
          <p>Loading documents...</p>
        )}

        {isError && (
          <p>Failed to load documents.</p>
        )}

        {!isLoading &&
          !isError &&
          documents?.length === 0 && (
            <p>No documents uploaded.</p>
          )}

        {documents?.map((document) => (
          <div
            key={document.id}
            className="flex items-center justify-between rounded border p-3 hover:bg-muted"
          >
            <Link
              href={`/documents/${document.id}`}
              className="min-w-0 flex-1"
            >
              <div className="break-words">
                📄 {document.filename}
              </div>

              <div className="mt-1 text-sm text-muted-foreground">
                Status: {document.status}
              </div>
            </Link>

            <button
              onClick={() => {
                if (
                  window.confirm(
                    `Delete ${document.filename}?`
                  )
                ) {
                  deleteMutation.mutate(document.id);
                }
              }}
              className="ml-3 rounded hover:bg-muted p-1"
              aria-label={`Delete ${document.filename}`}
              type="button"
            >
              <Trash2 className="size-4" />
            </button>
          </div>
        ))}
      </div>
    </main>
  );
}

