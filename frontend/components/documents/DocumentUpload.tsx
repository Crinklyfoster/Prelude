"use client";

import {
  type ChangeEvent,
  useRef,
  useState,
} from "react";
import { toast } from "sonner";

import { useUploadDocument } from "@/hooks/useUploadDocument";

export default function DocumentUpload() {
  const [selectedFiles, setSelectedFiles] =
    useState<File[]>([]);
  const fileInputRef =
    useRef<HTMLInputElement | null>(null);

  const uploadMutation = useUploadDocument();

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const files = Array.from(
      event.target.files ?? []
    );

    setSelectedFiles(files);
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) return;

    try {
      await Promise.all(
        selectedFiles.map((file) =>
          uploadMutation.mutateAsync(file)
        )
      );

      toast.success(
        `${selectedFiles.length} documents uploaded`
      );

      setSelectedFiles([]);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      const err = error as { response?: { status?: number } };
      if (err?.response?.status === 409) {
        toast.error("This PDF already exists in your library.");
      } else {
        toast.error("Upload failed");
      }
    }
  };

  return (
    <div className="space-y-4 rounded-lg border border-gray-300 bg-white p-4 text-black dark:border-gray-700 dark:bg-gray-900 dark:text-white">
      <label htmlFor="document-upload" className="block cursor-pointer rounded-lg border-2 border-dashed border-gray-300 p-8 text-center hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
        Click to select a document{" "}

        <input
          id="document-upload"
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf"
          className="hidden"
          onChange={handleFileChange}
        />
      </label>

      <div className="mt-2 text-sm">
        {!selectedFiles.length && (
          <p>No files selected</p>
        )}

        {selectedFiles.map((file) => (
          <p key={file.name}>{file.name}</p>
        ))}
      </div>

      <button
        type="button"
        onClick={handleUpload}
        disabled={
          !selectedFiles.length ||
          uploadMutation.isPending
        }
        className="rounded bg-gray-900 px-4 py-2 text-white hover:bg-gray-700 disabled:opacity-50 dark:bg-gray-100 dark:text-black dark:hover:bg-white"
      >
        {uploadMutation.isPending
          ? "Uploading..."
          : "Upload"}
      </button>
    </div>
  );
}
