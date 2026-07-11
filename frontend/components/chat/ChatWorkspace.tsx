"use client";

import {
  KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import { Paperclip, SendHorizontal, Square } from "lucide-react";
import { toast } from "sonner";

import MessageList from "@/components/chat/MessageList";
import { TypingIndicator } from "@/components/chat/TypingIndicator";

import { streamSendMessage } from "@/lib/chat";

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
}: Readonly<ChatWorkspaceProps>) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialQuestion =
    searchParams.get("q");

  const [input, setInput] =
    useState("");
  const [messages, setMessages] =
    useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const {
    data: history,

    isLoading: isLoadingMessages,
    isError: isMessagesError,
    isFetching: isFetchingMessages,
    refetch: refetchMessages,
  } = useMessages(sessionId);

  const bottomRef =
    useRef<HTMLDivElement>(null);
  const hasAutoSent = useRef(false);
  // Holds the current AbortController so the stop button can cancel streaming.
  const abortControllerRef = useRef<AbortController | null>(null);

  const uploadMutation =
    useUploadDocument();
  const fileInputRef =
    useRef<HTMLInputElement>(null);

  // Prefer local streaming state when we're actively streaming or have
  // optimistic messages; otherwise fall back to server-fetched history.
  const renderedMessages =
    isStreaming || messages.length > 0
      ? messages
      : history?.map((message) => ({
          role: message.role,
          content: message.content,
          timestamp: new Date(message.created_at ?? ""),
        })) ?? [];

  // Auto-scroll to bottom whenever messages change (covers history load).
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async (
    message?: string
  ) => {
    const question =
      message ?? input;

    if (!question.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    // If local state is empty, seed it from server history so the
    // existing conversation isn't dropped when we switch to local rendering.
    setMessages((prev) => {
      const base =
        prev.length === 0 && history
          ? history.map((m) => ({
              role: m.role,
              content: m.content,
              timestamp: new Date(m.created_at ?? ""),
            }))
          : prev;
      return [...base, userMessage];
    });

    setInput("");
    setIsStreaming(true);

    // Fresh AbortController for this request.
    const controller = new AbortController();
    abortControllerRef.current = controller;

    // Insert an empty assistant bubble so the user sees something immediately.
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", timestamp: new Date() } as Message,
    ]);

    try {
      for await (const event of streamSendMessage(
        { session_id: sessionId, question },
        controller.signal,
      )) {
        if (event.type === "token") {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated.at(-1);
            if (last?.role === "assistant") {
              updated[updated.length - 1] = {
                ...last,
                content: last.content + event.token,
              };
            }
            return updated;
          });
          // Scroll on every token so the bubble grows into view.
          scrollToBottom();
        } else if (event.type === "meta") {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated.at(-1);
            if (last?.role === "assistant") {
              updated[updated.length - 1] = {
                ...last,
                sources: event.sources,
              };
            }
            return updated;
          });
        }
      }
    } catch (err: unknown) {
      // AbortError is intentional (user clicked Stop) — don't show an error toast.
      if (err instanceof Error && err.name !== "AbortError") {
        toast.error("Failed to send message. Please try again.");
      }
      // Remove the empty placeholder on error (but keep partial content on abort).
      setMessages((prev) => {
        const updated = [...prev];
        const lastMsg = updated.at(-1);
        if (lastMsg?.role === "assistant" && lastMsg?.content === "") {
          updated.pop();
        }
        return updated;
      });
    } finally {
      abortControllerRef.current = null;
      setIsStreaming(false);
    }
  };

  useEffect(() => {
    if (!initialQuestion) return;
    if (hasAutoSent.current) return;

    hasAutoSent.current = true;

    handleSend(initialQuestion).catch(console.error);

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
      handleSend().catch(console.error);
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
              onClick={() => {
                refetchMessages().catch(console.error);
              }}
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
                <MessageList
                  messages={renderedMessages}
                  isStreaming={isStreaming}
                />
              )}

            </>
          )}

        {isStreaming &&
          renderedMessages.length > 0 &&
          renderedMessages.at(-1)?.content === "" && (
            <div className="mt-4">
              <TypingIndicator />
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

            {isStreaming ? (
              <button
                type="button"
                onClick={() => abortControllerRef.current?.abort()}
                className="rounded p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40"
                aria-label="Stop generating"
              >
                <Square className="size-5 fill-current" />
              </button>
            ) : (
              <button
                type="button"
                onClick={() => { handleSend().catch(console.error); }}
                disabled={!input.trim()}
                className="rounded p-2 hover:bg-muted disabled:opacity-50"
                aria-label="Send message"
              >
                <SendHorizontal className="size-5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
