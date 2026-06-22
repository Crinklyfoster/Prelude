export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
}

export interface CreateSessionResponse {
  session_id: string;
}

export interface Source {
  chunk_id: number;
  document_id: string;
  score: number;
  preview: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
}

export interface ChatRequest {
  session_id: string;
  question: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

