import { useMutation } from "@tanstack/react-query";

import { uploadDocument } from "@/lib/documents";

export function useUploadDocument() {
  return useMutation({
    mutationFn: uploadDocument,
  });
}