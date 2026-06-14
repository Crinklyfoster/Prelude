"use client";

import { useState } from "react";
import { toast } from "sonner";

import { useUploadDocument } from "@/hooks/useUploadDocument";

export default function DocumentUpload() {
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const uploadMutation = useUploadDocument();

  const handleUpload = () => {
    if (!selectedFile) return;

    uploadMutation.mutate(selectedFile, {
      onSuccess: () => {
        toast.success(
          "Document uploaded successfully"
        );

        setSelectedFile(null);
      },

      onError: () => {
        toast.error(
          "Failed to upload document"
        );
      },
    });
  };

  return (
    <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
      <input
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={(e) => {
          const file = e.target.files?.[0];

          if (file) {
            setSelectedFile(file);
          }
        }}
      />

      <button
        onClick={handleUpload}
        disabled={
          !selectedFile ||
          uploadMutation.isPending
        }
        className="px-4 py-2 rounded bg-foreground text-background disabled:opacity-50"
      >
        {uploadMutation.isPending
          ? "Uploading..."
          : "Upload"}
      </button>
    </div>
  );
}
