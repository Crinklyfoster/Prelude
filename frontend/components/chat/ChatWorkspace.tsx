"use client";

import {
  KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import { Paperclip, SendHorizontal } from "lucide-react";
import { toast } from "sonner";

import MessageList from "@/components/chat/MessageList";
import TypingIndicator from "@/components/chat/TypingIndicator";
import { useChat } from "@/hooks/useChat";
import { useMessages } from "@/hooks/useMessages";
import { useUploadDocument } from "@/hooks/useUploadDocument";
import { Message } from "@/types/message";

import {
  useRouter,
  useSearchParams,
} from "next/navigation";

export interface ChatWorkspaceProps {
  sessionId: string;
}

export default function ChatWorkspace({
  sessionId,
}: ChatWorkspaceProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialQuestion =
    searchParams.get("q");

  const [input, setInput] =
    useState("");
  const [messages, setMessages] =
    useState<Message[]>([]);

  const {
    data: history,

    isLoading: isLoadingMessages,
    isError: isMessagesError,
    isFetching: isFetchingMessages,
    refetch: refetchMessages,
  } = useMessages(sessionId);

  const chatMutation = useChat();
  const bottomRef =
    useRef<HTMLDivElement>(null);
  const hasAutoSent = useRef(false);

  const uploadMutation =
    useUploadDocument();
  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const renderedMessages =
    history?.map((message) => ({
      role: message.role,
      content: message.content,
      timestamp: new Date(message.created_at),
    })) ?? messages;









  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  const handleSend = async (
    message?: string
  ) => {
    chatMutation.reset();

    const question =
      message ?? input;

    if (!question.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
    ]);

    setInput("");

    try {
      const response =
        await chatMutation.mutateAsync({
          session_id: sessionId,
          question,
        });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages((prev) => [
        ...prev,
        assistantMessage,
      ]);
    } catch {
      // The mutation error is rendered below the message list.
    }
  };

  useEffect(() => {
    if (!initialQuestion) return;
    if (hasAutoSent.current) return;

    hasAutoSent.current = true;

    void handleSend(initialQuestion);

    router.replace(`/chat/${sessionId}`);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuestion, router, sessionId]);

  const handleKeyDown = (
    event: KeyboardEvent<HTMLInputElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.nativeEvent.isComposing
    ) {
      event.preventDefault();
      void handleSend();
    }
  };

  return (
<main className="mx-auto flex h-full min-h-0 w-full max-w-4xl flex-1 flex-col">
      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-8">
        {isLoadingMessages && (
          <div
            className="space-y-4"
            aria-label="Loading messages"
            aria-busy="true"
          >
            <div className="ml-auto h-20 w-2/3 animate-pulse rounded-lg bg-muted" />
            <div className="h-28 w-4/5 animate-pulse rounded-lg bg-muted" />
            <div className="ml-auto h-16 w-1/2 animate-pulse rounded-lg bg-muted" />
          </div>
        )}

        {isMessagesError && (
          <div className="py-12 text-center">
            <p className="font-medium">
              Failed to load messages.
            </p>

            <button
              type="button"
              onClick={() =>
                void refetchMessages()
              }
              disabled={isFetchingMessages}
              className="mt-4 rounded border border-gray-300 px-4 py-2 hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700"
            >
              {isFetchingMessages
                ? "Retrying..."
                : "Retry"}
            </button>
          </div>
        )}

        {!isLoadingMessages &&
          !isMessagesError && (
            <>
              {renderedMessages.length === 0 ? (
                <div className="mb-8 text-center">
                  <h1 className="text-4xl font-bold">
                    What would you like to ask?
                  </h1>

                  <p className="mt-3 text-muted-foreground">
                    Ask anything about your uploaded documents.
                  </p>
                </div>
              ) : (
                <MessageList messages={renderedMessages} />
              )}

            </>
          )}





        {chatMutation.isPending && (
          <div className="mt-4">
            <TypingIndicator />
          </div>
        )}

        {chatMutation.isError && (
          <div
            role="alert"
            className="mt-4 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"
          >
            Failed to send message. Please try again.
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="shrink-0 border-t border-gray-300 bg-white p-4 dark:border-gray-700 dark:bg-gray-950 sm:px-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            className="hidden"
            onChange={async (event) => {
              const files = Array.from(
                event.target.files ?? []
              );

              if (!files.length) return;

              try {
                for (const file of files) {
                  await uploadMutation.mutateAsync(file);
                }

                toast.success(
                  `${files.length} document(s) uploaded`
                );

                if (fileInputRef.current) {
                  fileInputRef.current.value = "";
                }
              } catch (error) {
                console.error("UPLOAD ERROR:", error);
                toast.error(
                  "Failed to upload document(s)"
                );
              }
            }}
          />

          <div className="flex w-full items-center gap-2 rounded-xl border border-gray-300 bg-white p-3 dark:border-gray-700 dark:bg-gray-900">
            <button
              type="button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={uploadMutation.isPending}
              className="rounded p-2 hover:bg-muted disabled:opacity-50"
              aria-label="Upload documents"
            >
              <Paperclip className="size-5" />
            </button>

            <input
              autoFocus
              value={input}
              onChange={(e) =>
                setInput(e.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask about your documents..."
              className="flex-1 bg-transparent text-black outline-none dark:text-white"
            />

            <button
              type="button"
              onClick={() => void handleSend()}
              disabled={
                chatMutation.isPending ||
                !input.trim()
              }
              className="rounded p-2 hover:bg-muted disabled:opacity-50"
              aria-label="Send message"
            >
              <SendHorizontal className="size-5" />
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}

