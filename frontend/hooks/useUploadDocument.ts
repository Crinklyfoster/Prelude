import { useMutation, useQueryClient } from "@tanstack/react-query";

import { uploadDocument } from "@/lib/documents";

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: uploadDocument,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["documents"],
      });
    },
  });
}