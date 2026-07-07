import { ReactNode } from "react";

import { ChatHeader } from "./ChatHeader";

interface Props {
  children: ReactNode;
}

export function ChatLayout({
  children,
}: Props) {
  return (
    <div className="flex h-screen flex-col">
      <ChatHeader />

      <main className="flex flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
}

