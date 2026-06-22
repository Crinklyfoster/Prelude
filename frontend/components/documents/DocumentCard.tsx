"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Document } from "@/types/document";
import { useCreateSession } from "@/hooks/useCreateSession";
import { useDeleteDocument } from "@/hooks/useDeleteDocument";

interface DocumentCardProps {
  document: Document;
}

const statusStyles = {
  uploaded: "bg-blue-500/10 text-blue-500",
  processing: "bg-yellow-500/10 text-yellow-500",
  processed: "bg-green-500/10 text-green-500",
};

export default function DocumentCard({
  document,
}: DocumentCardProps) {
  const router = useRouter();
  const createSessionMutation = useCreateSession();
  const deleteMutation = useDeleteDocument();

  return (
    <div className="rounded-lg border border-gray-300 bg-white p-4 text-black dark:border-gray-700 dark:bg-gray-900 dark:text-white">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Link
          href={`/documents/${document.id}`}
          className="min-w-0 flex-1"
        >
          <p className="break-words font-medium">
            {document.filename}
          </p>

          <span
            className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
              statusStyles[
                document.status as keyof typeof statusStyles
              ] ?? "bg-foreground/10 text-muted-foreground"
            }`}
          >
            {document.status}
          </span>

          <p className="text-xs text-muted-foreground mt-2">
            Uploaded{" "}
            {new Date(
              document.uploaded_at
            ).toLocaleString()}
          </p>
        </Link>

        <div className="flex flex-wrap items-center gap-2 sm:justify-end">
          <button
            onClick={async () => {
              try {
                const result =
                  await createSessionMutation.mutateAsync();

                toast.success(
                  "Chat session created"
                );

                router.push(
                  `/chat/${result.session_id}`
                );
              } catch {
                toast.error(
                  "Failed to start chat"
                );
              }
            }}
            disabled={createSessionMutation.isPending}
            className="rounded border border-gray-300 bg-white px-3 py-1 text-black hover:bg-gray-100 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:bg-gray-800"
          >
            Start Chat
          </button>

          <button
            onClick={() =>
              deleteMutation.mutate(document.id, {
                onSuccess: () => {
                  toast.success(
                    "Document deleted successfully"
                  );
                },

                onError: () => {
                  toast.error(
                    "Failed to delete document"
                  );
                },
              })
            }
            disabled={deleteMutation.isPending}
            className="rounded border border-gray-300 bg-white px-3 py-1 text-black hover:bg-gray-100 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white dark:hover:bg-gray-800"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
