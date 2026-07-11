import { api } from "@/lib/api";
import type {
  ChatRequest,
  ChatResponse,
  ChatSession,
  CreateSessionResponse,
  ChatMessage,
} from "@/types/chat_request";

export type StreamChatEvent =
  | { type: "token"; token: string }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  | { type: "meta"; sources: ChatResponse["sources"]; final: boolean; provider_meta?: any };

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

export async function* streamSendMessage(
  payload: ChatRequest,
  signal?: AbortSignal,
): AsyncGenerator<StreamChatEvent, void, unknown> {
  const token = (await import("@/lib/auth")).getToken();

  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/chat/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
      signal,
    }
  );

  if (!res.ok || !res.body) {
    throw new Error(`Stream request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE messages are separated by double newline.
    while (true) {
      const idx = buffer.indexOf("\n\n");
      if (idx === -1) break;

      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);

      const event = parseSSEEvent(raw);
      if (event) {
        yield event;
      }
    }
  }
}

function parseSSEEvent(raw: string): StreamChatEvent | null {
  const lines = raw.split("\n");
  const eventLine = lines.find((l) => l.startsWith("event:"));
  const dataLine = lines.find((l) => l.startsWith("data:"));

  const eventName = eventLine
    ? eventLine.replace("event:", "").trim()
    : "message";

  const dataStr = dataLine
    ? dataLine.replace("data:", "").trim()
    : "{}";

  const data = JSON.parse(dataStr);

  if (eventName === "token") {
    return { type: "token", token: data.token ?? "" };
  }
  
  if (eventName === "meta") {
    return {
      type: "meta",
      sources: data.sources ?? [],
      final: Boolean(data.final),
      provider_meta: data.provider_meta,
    };
  }
  
  return null;
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
