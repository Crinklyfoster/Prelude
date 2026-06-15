import { useMutation } from "@tanstack/react-query";

import { sendMessage } from "@/lib/chat";

export function useChat() {
  return useMutation({
    mutationFn: sendMessage,
  });
}
