"use client";

import DocumentList from "@/components/documents/DocumentList";
import DocumentUpload from "@/components/documents/DocumentUpload";
import { useDocuments } from "@/hooks/useDocuments";

export default function DocumentsPage() {
  const { data, isLoading, isError } = useDocuments();

  if (isLoading) {
    return (
      <main className="p-8">
        <h1 className="text-3xl font-bold">
          Documents
        </h1>

        <p className="mt-4">
          Loading documents...
        </p>
      </main>
    );
  }

  if (isError) {
    return (
      <main className="p-8">
        <h1 className="text-3xl font-bold">
          Documents
        </h1>

        <p className="mt-4 text-red-500">
          Failed to load documents
        </p>
      </main>
    );
  }

  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold">
        Documents
      </h1>

      <div className="mt-6">
        <DocumentUpload />
        <DocumentList documents={data ?? []} />
      </div>
    </main>
  );
}
