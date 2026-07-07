export interface Source {
  chunk_id: number;
  document_id: string;
  score: number;
  preview: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

