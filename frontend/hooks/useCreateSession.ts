import { useMutation } from "@tanstack/react-query";

import { createSession } from "@/lib/chat";

export function useCreateSession() {
  return useMutation({
    mutationFn: createSession,
  });
}
