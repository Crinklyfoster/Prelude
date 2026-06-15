import { useQuery } from "@tanstack/react-query";

import { getDocument } from "@/lib/documents";

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ["document", documentId],
    queryFn: () => getDocument(documentId),
    enabled: !!documentId,
  });
}
