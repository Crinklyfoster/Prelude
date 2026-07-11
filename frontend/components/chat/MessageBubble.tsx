"use client";

import { useState } from "react";

import { Message } from "@/types/message";

import { SourceCard } from "./SourceCard";

interface MessageBubbleProps {
  message: Message;
  /** When true, renders a blinking cursor after the content (streaming assistant message). */
  isStreaming?: boolean;
}

export default function MessageBubble({
  message,
  isStreaming = false,
}: Readonly<MessageBubbleProps>) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === "user";
  const isEmpty = message.content === "" && !isUser;

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`min-w-0 max-w-[92%] break-words rounded-lg px-4 py-3 sm:max-w-[80%] ${
          isUser
            ? "bg-blue-500 text-white"
            : "bg-gray-100 text-black dark:bg-gray-800 dark:text-white"
        }`}
      >
        {/* Content + blinking cursor while streaming */}
        <span>
          {message.content}
          {isStreaming && !isUser && (
            <span
              aria-hidden="true"
              className="ml-0.5 inline-block animate-pulse select-none font-normal"
            >
              ▌
            </span>
          )}
        </span>

        {!isEmpty && message.sources?.length ? (
          <div className="mt-3">
            <button
              onClick={() => setShowSources(!showSources)}
              className="text-sm underline"
            >
              {showSources
                ? "Hide Sources"
                : `Show Sources (${message.sources.length})`}
            </button>

            {showSources && (
              <div className="mt-2 space-y-2">
                {message.sources.map((source) => (
                  <SourceCard
                    key={`${source.document_id}-${source.chunk_id}`}
                    preview={source.preview}
                    score={source.score}
                  />
                ))}
              </div>
            )}
          </div>
        ) : null}

        {/* Provider Badge */}
        {!isEmpty && message.provider && (
          <div className={`mt-3 inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium uppercase tracking-wider ${isUser ? "bg-blue-600 text-blue-100" : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300"}`}>
            {message.provider}
            {message.latencyMs !== undefined ? ` ${(message.latencyMs / 1000).toFixed(1)} s` : ""}
          </div>
        )}

        {/* Hide the timestamp on the empty placeholder bubble */}
        {!isEmpty && (
          <p
            className={`mt-2 text-xs ${
              isUser ? "text-blue-100" : "text-muted-foreground"
            }`}
          >
            {message.timestamp.toLocaleTimeString([], {
              hour: "numeric",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>
    </div>
  );
}
