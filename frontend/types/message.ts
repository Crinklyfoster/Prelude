import { Source } from "./chat";

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  timestamp: Date;
  provider?: string;
  latencyMs?: number;
}
