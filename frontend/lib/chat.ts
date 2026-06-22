import { api } from "@/lib/api";
import {
  ChatMessage,
  ChatRequest,
  ChatResponse,
  ChatSession,
  CreateSessionResponse,
} from "@/types/chat";

export async function createSession(): Promise<CreateSessionResponse> {
  const response =
    await api.post<CreateSessionResponse>(
      "/chat/sessions"
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

export async function getSessions(): Promise<ChatSession[]> {
  const response = await api.get<ChatSession[]>("/chat/sessions");

  return response.data;
}

export async function getMessages(
  sessionId: string
): Promise<ChatMessage[]> {
  const response = await api.get<ChatMessage[]>(
    `/chat/sessions/${sessionId}/messages`
  );

  return response.data;
}

export async function renameSession(
  sessionId: string,
  title: string
): Promise<ChatSession> {
  const response = await api.patch<ChatSession>(
    `/chat/sessions/${sessionId}`,
    { title }
  );

  return response.data;
}

export async function deleteSession(
  sessionId: string
): Promise<void> {
  await api.delete(`/chat/sessions/${sessionId}`);
}
