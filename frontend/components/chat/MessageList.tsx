import { Message } from "@/types/message";

import MessageBubble from "./MessageBubble";

interface MessageListProps {
  messages: Message[];
  /** When true, the last message renders a blinking cursor. */
  isStreaming?: boolean;
}

export default function MessageList({
  messages,
  isStreaming = false,
}: Readonly<MessageListProps>) {
  if (messages.length === 0) {
    return (
      <div className="py-12 text-center">
        <h2 className="text-2xl font-semibold">
          Start a conversation
        </h2>

        <p className="mt-2 text-muted-foreground">
          Ask a question about this document.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <MessageBubble
          key={`${message.role}-${message.timestamp.getTime()}`}
          message={message}
          isStreaming={isStreaming && index === messages.length - 1}
        />
      ))}
    </div>
  );
}
