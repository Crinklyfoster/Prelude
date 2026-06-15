import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { deleteSession } from "@/lib/chat";

export function useDeleteSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteSession,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sessions"],
      });
    },
  });
}
