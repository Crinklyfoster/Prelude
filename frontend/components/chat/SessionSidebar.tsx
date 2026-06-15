"use client";

import { Pencil, Trash2 } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

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

export default function SessionSidebar() {
  const { sessionId } = useParams<{
    sessionId: string;
  }>();
  const { data, isLoading } = useSessions();
  const renameMutation = useRenameSession();
  const deleteMutation = useDeleteSession();

  const handleRename = (
    id: string,
    currentTitle: string
  ) => {
    const title = window.prompt(
      "Enter new title:",
      currentTitle
    )?.trim();

    if (!title || title === currentTitle) return;

    renameMutation.mutate({
      sessionId: id,
      title,
    });
  };

  const handleDelete = (id: string) => {
    if (!window.confirm("Delete this session?")) return;

    deleteMutation.mutate(id);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="w-72 border-r p-4">
      <h2 className="font-bold">Chats</h2>

      <div className="mt-4 space-y-2">
        {data?.map((session) => {
          const isActive = session.id === sessionId;

          return (
            <div
              key={session.id}
              className={`rounded border p-2 ${
                isActive ? "bg-muted font-semibold" : ""
              }`}
            >
              <div className="flex items-start gap-2">
                <Link
                  href={`/chat/${session.id}`}
                  className="min-w-0 flex-1"
                >
                  <span className="block truncate">
                    {session.title}
                  </span>

                  <span className="mt-1 block text-xs font-normal text-muted-foreground">
                    Created:{" "}
                    {formatCreatedAt(session.created_at)}
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
                  disabled={renameMutation.isPending}
                  aria-label={`Rename ${session.title}`}
                  className="rounded p-1 hover:bg-background disabled:opacity-50"
                >
                  <Pencil className="size-4" />
                </button>

                <button
                  type="button"
                  onClick={() => handleDelete(session.id)}
                  disabled={deleteMutation.isPending}
                  aria-label={`Delete ${session.title}`}
                  className="rounded p-1 hover:bg-background disabled:opacity-50"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
