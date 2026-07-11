"use client";

import ReactMarkdown, { Components } from "react-markdown";
import remarkGfm from "remark-gfm";

const markdownComponents: Components = {
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
};


import { ChatMessage as Message } from "@/types/chat";

import { SourceCard } from "./SourceCard";


interface Props {
  message: Message;
}

export function ChatMessage({
  message,
}: Readonly<Props>) {
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
            components={markdownComponents}
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

