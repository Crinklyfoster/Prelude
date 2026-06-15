import { useQuery } from "@tanstack/react-query";

import { getSessions } from "@/lib/chat";

export function useSessions() {
  return useQuery({
    queryKey: ["sessions"],
    queryFn: getSessions,
  });
}
