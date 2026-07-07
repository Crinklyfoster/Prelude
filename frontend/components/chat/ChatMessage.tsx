"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";


import { ChatMessage as Message } from "@/types/chat";

import { SourceCard } from "./SourceCard";


interface Props {
  message: Message;
}

export function ChatMessage({
  message,
}: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-3xl rounded-xl px-4 py-3 ${
          isUser ? "bg-blue-600 text-white" : "bg-muted"
        }`}
      >
        <div className="prose prose-neutral dark:prose-invert max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              table({ ...props }) {
                return (
                  <div className="overflow-x-auto">
                    <table {...props} />
                  </div>
                );
              },
              a({ ...props }) {
                return (
                  <a
                    {...props}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 underline"
                  />
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {message.sources?.map((source) => (
          <SourceCard
            key={source.chunk_id}
            preview={source.preview}
            score={source.score}
          />
        ))}
      </div>
    </div>
  );
}

