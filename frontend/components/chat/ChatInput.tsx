"use client";

import { useState } from "react";

type LLMProvider = "groq" | "gemini";
type ProviderOption = "" | LLMProvider;

interface Props {
  loading: boolean;
  onSend: (message: string, provider?: LLMProvider) => void;
}

export function ChatInput({
  loading,
  onSend,
}: Readonly<Props>) {
  const [message, setMessage] = useState("");
  const [provider, setProvider] = useState<ProviderOption>(
    () => {
      if (typeof window !== "undefined") {
        return (localStorage.getItem("preferred_provider") as ProviderOption) ?? "";
      }
      return "";
    }
  );

  function submit() {
    if (!message.trim()) return;

    onSend(message, provider || undefined);

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
          placeholder="Ask me anything..."
          className="flex-1 rounded-lg border p-3"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              submit();
            }
          }}
        />

        <select
          value={provider}
          onChange={(e) => {
            const value = e.target.value as ProviderOption;
            setProvider(value);
            if (typeof window !== "undefined") {
              localStorage.setItem("preferred_provider", value);
            }
          }}
          className="rounded-lg border px-3 py-2"
        >
          <option value="">Auto</option>
          <option value="groq">Groq · Llama 3.3 70B</option>
          <option value="gemini">Gemini · Gemini Flash</option>
        </select>

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

