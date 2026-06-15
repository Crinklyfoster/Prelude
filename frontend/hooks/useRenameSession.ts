import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { renameSession } from "@/lib/chat";

export function useRenameSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sessionId,
      title,
    }: {
      sessionId: string;
      title: string;
    }) => renameSession(sessionId, title),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sessions"],
      });
    },
  });
}
