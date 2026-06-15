import { Message } from "@/types/message";

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
          <div className="mt-4 space-y-2">
            {message.sources.map((source, index) => (
              <div
                key={index}
                className="border rounded p-2 text-sm"
              >
                <p className="font-medium">
                  Source {index + 1}
                </p>

                <p className="text-xs opacity-75">
                  Document: {source.document_id}
                </p>

                <p className="text-xs opacity-75">
                  Confidence:{" "}
                  {(source.score * 100).toFixed(1)}%
                </p>

                <p className="mt-2">{source.preview}</p>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}
