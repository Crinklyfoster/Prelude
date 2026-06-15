"use client";

import { useParams, useSearchParams } from "next/navigation";
import {
  KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import MessageList from "@/components/chat/MessageList";
import TypingIndicator from "@/components/chat/TypingIndicator";
import { useChat } from "@/hooks/useChat";
import { Message } from "@/types/message";

export default function ChatPage() {
  const { sessionId } = useParams<{
    sessionId: string;
  }>();
  const searchParams = useSearchParams();
  const documentId = searchParams.get("documentId");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const chatMutation = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    if (!documentId) {
      alert("Document ID missing");
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
    ]);

    const question = input;

    setInput("");

    try {
      const response =
        await chatMutation.mutateAsync({
          session_id: sessionId,
          document_id: documentId,
          question,
        });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages((prev) => [
        ...prev,
        assistantMessage,
      ]);
    } catch (error) {
      console.error(error);
    }
  };

  const handleKeyDown = (
    event: KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.nativeEvent.isComposing
    ) {
      event.preventDefault();
      void handleSend();
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col">
      <header className="shrink-0 px-8 pt-8">
        <h1 className="text-3xl font-bold">
          Chat
        </h1>

        <p className="mt-2 text-sm text-muted-foreground">
          Session: {sessionId}
          {documentId && ` | Document: ${documentId}`}
        </p>
      </header>

      <div className="flex-1 px-8 py-6">
        <MessageList messages={messages} />

        {chatMutation.isPending && (
          <div className="mt-4">
            <TypingIndicator />
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="shrink-0 border-t bg-background p-4 sm:px-8">
        <div className="flex items-end gap-3">
          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask a question..."
            rows={3}
            className="min-h-20 flex-1 resize-none rounded border p-3"
          />

          <button
            type="button"
            onClick={() => void handleSend()}
            disabled={
              chatMutation.isPending || !input.trim()
            }
            className="rounded border px-4 py-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </main>
  );
}
