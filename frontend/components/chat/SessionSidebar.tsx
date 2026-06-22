"use client";

import { Pencil, Trash2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import ThemeToggle from "@/components/layout/theme-toggle";
import { useCreateSession } from "@/hooks/useCreateSession";
import { useDeleteSession } from "@/hooks/useDeleteSession";
import { useRenameSession } from "@/hooks/useRenameSession";
import { useSessions } from "@/hooks/useSessions";

function formatCreatedAt(createdAt: string) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(createdAt));
}

function displaySessionTitle(title: string) {
  return title.trim().toLowerCase() === "new chat"
    ? "Untitled Chat"
    : title;
}

export default function SessionSidebar() {
  const [collapsed, setCollapsed] = useState(false);

  const router = useRouter();
  const { sessionId } = useParams<{
    sessionId?: string;
  }>();

  const {
    data,
    isLoading,
    isError,
    isFetching,
    refetch,
  } = useSessions();

  const createSessionMutation =
    useCreateSession();

  const renameMutation = useRenameSession();
  const deleteMutation = useDeleteSession();

  useEffect(() => {
    if (isError) {
      toast.error("Failed to load sessions");
    }
  }, [isError]);

  const handleRename = (
    id: string,
    currentTitle: string
  ) => {
    const title = window.prompt(
      "Enter session title",
      currentTitle
    )?.trim();

    if (!title || title === currentTitle) return;

    renameMutation.mutate(
      {
        sessionId: id,
        title,
      },
      {
        onSuccess: () => {
          toast.success("Session renamed");
        },

        onError: () => {
          toast.error("Failed to rename session");
        },
      }
    );
  };

  const handleDelete = (
    id: string,
    title: string
  ) => {
    const sessionTitle = displaySessionTitle(title);
    if (
      !window.confirm(
        `Delete "${sessionTitle}"? This cannot be undone.`
      )
    ) {
      return;
    }

    deleteMutation.mutate(id, {
      onSuccess: () => {
        toast.success("Chat session deleted");

        if (id === sessionId) {
          router.push("/chat");
        }
      },

      onError: () => {
        toast.error("Failed to delete chat session");
      },
    });
  };

  return (
    <aside
      className={`shrink-0 border-r transition-all duration-300
      ${collapsed ? "w-16" : "w-72"}`}
    >
      <button
        type="button"
        onClick={() => setCollapsed(!collapsed)}
        className="mb-4 w-full rounded p-2 hover:bg-muted"
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        ☰
      </button>

      <div className="px-4">
        {!collapsed && (
          <>
            <div className="mb-4">
              <ThemeToggle />
            </div>

            <button
              type="button"
              className="mb-4 w-full rounded border border-gray-300 p-2 text-center font-medium hover:bg-muted dark:border-gray-700"
              disabled={createSessionMutation.isPending}
              onClick={() => {
                createSessionMutation.mutate(
                  undefined,
                  {
                    onSuccess: (data) => {
                      router.push(
                        `/chat/${data.session_id}`
                      );
                    },

                    onError: () => {
                      toast.error(
                        "Failed to create chat session"
                      );
                    },
                  }
                );
              }}
            >
              + New Chat
            </button>

            <h2 className="font-bold">Chats</h2>
          </>
        )}

        {!collapsed && (
          <div className="mt-4 space-y-2">
            {isLoading && (
              <div
                className="space-y-2"
                aria-label="Loading chat sessions"
                aria-busy="true"
              >
                {[1, 2, 3, 4].map((item) => (
                  <div
                    key={item}
                    className="h-16 animate-pulse rounded bg-muted"
                  />
                ))}
              </div>
            )}

            {isError && (
              <div className="py-6 text-center">
                <p className="text-sm font-medium">
                  Failed to load sessions.
                </p>

                <button
                  type="button"
                  onClick={() => void refetch()}
                  disabled={isFetching}
                  className="mt-3 rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700"
                >
                  {isFetching ? "Retrying..." : "Retry"}
                </button>
              </div>
            )}

            {!isLoading &&
              !isError &&
              !data?.length && (
                <div className="py-6 text-center">
                  <p className="font-medium">
                    No chat sessions yet
                  </p>

                  <p className="mt-2 text-sm text-muted-foreground">
                    Create a session from a document.
                  </p>
                </div>
              )}

            {!isLoading && !isError &&
              data?.map((session) => {
                const isActive =
                  session.id === sessionId;
                const sessionTitle = displaySessionTitle(
                  session.title
                );

                return (
                  <div
                    key={session.id}
                    className={`block rounded border border-gray-300 p-2 dark:border-gray-700 ${
                      isActive
                        ? "bg-muted font-semibold"
                        : ""
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <Link
                        href={`/chat/${session.id}`}
                        className="min-w-0 flex-1"
                      >
                        <span className="block truncate">
                          {sessionTitle}
                        </span>

                        <span className="mt-1 block text-xs font-normal text-muted-foreground">
                          Created:{" "}
                          {formatCreatedAt(
                            session.created_at
                          )}
                        </span>
                      </Link>

                      <button
                        type="button"
                        onClick={() =>
                          handleRename(
                            session.id,
                            session.title
                          )
                        }
                        disabled={
                          renameMutation.isPending
                        }
                        aria-label={`Rename ${sessionTitle}`}
                        className="rounded p-1 hover:bg-gray-200 disabled:opacity-50 dark:hover:bg-gray-700"
                      >
                        <Pencil className="size-4" />
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          handleDelete(
                            session.id,
                            session.title
                          )
                        }
                        disabled={
                          deleteMutation.isPending
                        }
                        aria-label={`Delete ${sessionTitle}`}
                        className="rounded p-1 hover:bg-gray-200 disabled:opacity-50 dark:hover:bg-gray-700"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
          </div>
        )}

        {!collapsed && (
          <>
            <hr className="my-4 border-gray-300 dark:border-gray-700" />

            <h2 className="mb-2 font-bold">
              Workspace
            </h2>

            <Link
              href="/library"
              className="block rounded border border-gray-300 p-2 hover:bg-muted dark:border-gray-700"
            >
              Library
            </Link>

          </>
        )}
      </div>
    </aside>
  );
}


