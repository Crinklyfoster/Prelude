"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useState } from "react";

import { useChat } from "@/hooks/useChat";

export default function ChatPage() {
  const { sessionId } = useParams<{
    sessionId: string;
  }>();
  const searchParams = useSearchParams();
  const documentId = searchParams.get("documentId");
  const [input, setInput] = useState("");
  const chatMutation = useChat();

  const handleSend = async () => {
    if (!input.trim()) return;

    if (!documentId) {
      alert("Document ID missing");
      return;
    }

    try {
      const response =
        await chatMutation.mutateAsync({
          session_id: sessionId,
          document_id: documentId,
          question: input,
        });

      console.log(response);

      setInput("");
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
          {chatMutation.isPending
            ? "Thinking..."
            : "Send"}
        </button>
      </div>
    </main>
  );
}
