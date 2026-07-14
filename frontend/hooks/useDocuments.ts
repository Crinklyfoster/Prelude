import { useQuery } from "@tanstack/react-query";
import { getDocuments } from "@/lib/documents";
import { Document } from "@/types/document";

export function useDocuments() {
  return useQuery<Document[]>({
    queryKey: ["documents"],
    queryFn: getDocuments,
    refetchInterval: (query) => {
      const hasProcessing = query.state.data?.some(
        (doc) => doc.status === "processing"
      );
      return hasProcessing ? 3000 : false;
    },
  });
}