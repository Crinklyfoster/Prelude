export interface ChatSession {
  id: string;
  document_id: string;
  title: string;
  created_at: string;
}

export interface CreateSessionResponse {
  session_id: string;
  document_id: string;
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
  document_id: string;
  question: string;
}
