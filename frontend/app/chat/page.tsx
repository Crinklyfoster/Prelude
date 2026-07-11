"use client";

import { Paperclip, SendHorizontal } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { useCreateSession } from "@/hooks/useCreateSession";
import { useUploadDocument } from "@/hooks/useUploadDocument";

import { useRouter } from "next/navigation";

import SessionSidebar from "@/components/chat/SessionSidebar";
import { AuthGuard } from "@/components/auth/AuthGuard";

export default function ChatHomePage() {
  const router = useRouter();

  const [question, setQuestion] = useState("");
  const [provider, setProvider] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("preferred_provider") ?? "auto";
    }
    return "auto";
  });

  const createSessionMutation = useCreateSession();

  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useUploadDocument();

  const handleSend = () => {
    const trimmed = question.trim();
    if (!trimmed) return;

    createSessionMutation.mutate(undefined, {
      onSuccess: (data) => {
        // Preserve the landing UI until navigation completes,
        // and avoid any visible “old page” jump.
        setQuestion("");
        router.push(
          `/chat/${data.session_id}?q=${encodeURIComponent(trimmed)}`
        );
      },
    });
  };

  return (
    <AuthGuard>
      <div className="flex h-screen">
        <SessionSidebar />

        <main className="flex-1">
          <main className="flex h-[calc(100dvh-57px)] items-center justify-center">
            <div className="w-full max-w-3xl px-6">
              <h1 className="mb-8 text-center text-4xl font-bold">
                What would you like to ask?
              </h1>

              <div className="flex items-center gap-2 rounded-xl border p-3">
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf"
                  className="hidden"
                  onChange={async (event) => {
                    const files = Array.from(event.target.files ?? []);

                    console.log(
                      "Selected files:",
                      files.map((f) => f.name)
                    );

                    if (!files.length) return;

                    try {
                      for (const file of files) {
                        console.log("Uploading:", file.name);
                        await uploadMutation.mutateAsync(file);
                      }

                      toast.success(`${files.length} document(s) uploaded`);

                      if (fileInputRef.current) {
                        fileInputRef.current.value = "";
                      }
                    } catch (error) {
                      console.error("UPLOAD ERROR:", error);
                      const err = error as { response?: { status?: number } };
                      if (err?.response?.status === 409) {
                        toast.error("This PDF already exists in your library.");
                      } else {
                        toast.error("Failed to upload document(s)");
                      }
                    }
                  }}
                />

                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="rounded p-2 hover:bg-muted"
                >
                  <Paperclip className="size-5" />
                </button>

                <select
                  value={provider}
                  onChange={(e) => {
                    const val = e.target.value;
                    setProvider(val);
                    localStorage.setItem("preferred_provider", val);
                  }}
                  className="rounded border border-gray-200 bg-gray-50 px-2 py-1 text-sm outline-none dark:border-gray-700 dark:bg-gray-800"
                >
                  <option value="auto">Auto</option>
                  <option value="groq">Groq</option>
                  <option value="gemini">Gemini</option>
                </select>

                <input
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleSend();
                    }
                  }}
                  placeholder="Ask about your documents..."
                  className="flex-1 bg-transparent outline-none"
                />

                <button
                  type="button"
                  onClick={handleSend}
                  disabled={
                    !question.trim() || createSessionMutation.isPending
                  }
                  className="rounded p-2 hover:bg-muted disabled:opacity-50"
                >
                  <SendHorizontal className="size-5" />
                </button>
              </div>
            </div>
          </main>
        </main>
      </div>
    </AuthGuard>
  );
}

