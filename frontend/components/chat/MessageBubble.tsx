import { Message } from "@/types/message";

import SourceCard from "./SourceCard";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({
  message,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-blue-500 text-white"
            : "bg-muted"
        }`}
      >
        {message.content}

        {message.sources?.length ? (
          <div className="mt-4">
            {message.sources.map((source, index) => (
              <SourceCard
                key={index}
                source={source}
                index={index}
              />
            ))}
          </div>
        ) : null}

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
      </div>
    </div>
  );
}
