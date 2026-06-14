"use client";

import { toast } from "sonner";

import { Document } from "@/types/document";
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
  const deleteMutation = useDeleteDocument();

  return (
    <div className="border border-border rounded-lg p-4 bg-card">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium">
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
        </div>

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
          className="px-3 py-1 rounded border border-border"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
