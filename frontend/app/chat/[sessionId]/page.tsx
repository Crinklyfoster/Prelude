"use client";

import { useParams } from "next/navigation";

import ChatWorkspace from "@/components/chat/ChatWorkspace";
import SessionSidebar from "@/components/chat/SessionSidebar";

export default function ChatPage() {
  const { sessionId } = useParams<{
    sessionId: string;
  }>();

  return (
    <div className="flex h-screen">
      <SessionSidebar />

      <main className="flex-1">
        <ChatWorkspace sessionId={sessionId} />
      </main>
    </div>
  );
}


