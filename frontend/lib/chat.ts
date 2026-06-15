import { api } from "@/lib/api";
import {
  ChatRequest,
  ChatResponse,
  CreateSessionResponse,
} from "@/types/chat";

export async function createSession(
  documentId: string
): Promise<CreateSessionResponse> {
  const response = await api.post<CreateSessionResponse>(
    "/chat/sessions",
    null,
    {
      params: {
        document_id: documentId,
      },
    }
  );

  return response.data;
}

export async function sendMessage(
  payload: ChatRequest
): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>(
    "/chat",
    payload
  );

  return response.data;
}
