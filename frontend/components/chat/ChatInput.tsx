"use client";

import { useState } from "react";

interface Props {
  loading: boolean;
  onSend: (message: string) => void;
}

export function ChatInput({
  loading,
  onSend,
}: Readonly<Props>) {
  const [message, setMessage] = useState("");

  function submit() {
    if (!message.trim()) return;

    onSend(message);

    setMessage("");
  }

  return (
    <div className="border-t p-4">
      <div className="flex gap-3">
        <input
          value={message}
          onChange={(e) =>
            setMessage(e.target.value)
          }
          placeholder="Ask anything about your documents..."
          className="flex-1 rounded-lg border p-3"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              submit();
            }
          }}
        />

        <button
          disabled={loading}
          onClick={submit}
          className="rounded-lg bg-blue-600 px-5 text-white"
        >
          Send
        </button>
      </div>
    </div>
  );
}

