import { ChatMessage as Message } from "@/types/chat";

import { ChatMessage } from "./ChatMessage";

interface Props {
  messages: Message[];
}

export function ChatMessages({
  messages,
}: Props) {
  return (
    <div className="flex flex-1 flex-col gap-6 overflow-y-auto p-6">
      {messages.map((message) => (
        <ChatMessage
          key={message.id}
          message={message}
        />
      ))}
    </div>
  );
}

