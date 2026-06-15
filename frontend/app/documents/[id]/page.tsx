"use client";

import { use } from "react";

import { useDocument } from "@/hooks/useDocument";

interface Props {
  params: Promise<{
    id: string;
  }>;
}

export default function DocumentDetailsPage({
  params,
}: Props) {
  const { id } = use(params);
  const { data, isLoading } = useDocument(id);

  if (isLoading) {
    return (
      <main className="p-8">
        Loading...
      </main>
    );
  }

  if (!data) {
    return (
      <main className="p-8">
        Document not found
      </main>
    );
  }

  return (
    <main className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold">
        {data.filename}
      </h1>

      <div className="mt-8 space-y-4">
        <div>
          <strong>ID:</strong> {data.id}
        </div>

        <div>
          <strong>Status:</strong>{" "}
          {data.status}
        </div>

        <div>
          <strong>Uploaded:</strong>{" "}
          {new Date(
            data.uploaded_at
          ).toLocaleString()}
        </div>

        <div>
          <strong>File Path:</strong>{" "}
          {data.file_path}
        </div>
      </div>
    </main>
  );
}
