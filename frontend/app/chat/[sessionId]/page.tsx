"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

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
      };

      setMessages((prev) => [
        ...prev,
        assistantMessage,
      ]);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <main className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold">
        Chat
      </h1>

      <p className="mt-2 text-sm text-muted-foreground">
        Session: {sessionId}
        {documentId && ` | Document: ${documentId}`}
      </p>

      <div className="mt-8">
        <MessageList messages={messages} />

        {chatMutation.isPending && (
          <div className="mt-4">
            <TypingIndicator />
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="mt-8">
        <textarea
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          className="w-full border rounded p-3"
        />

        <button
          onClick={handleSend}
          disabled={chatMutation.isPending}
          className="mt-4 border px-4 py-2 rounded"
        >
          Send
        </button>
      </div>
    </main>
  );
}
