"use client";

import { useSyncExternalStore } from "react";
import { useTheme } from "next-themes";

const themeOptions = [
  { value: "light", label: "☀️ Light" },
  { value: "dark", label: "🌙 Dark" },
  { value: "system", label: "💻 System" },
] as const;

const emptySubscribe = () => () => {};

export default function Navbar() {
  const mounted = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  );
  const { theme, setTheme } = useTheme();

  return (
    <nav className="flex items-center justify-between border-b border-border bg-card px-8 py-4">
      <span className="font-semibold">
        Enterprise RAG Assistant
      </span>

      <div
        className="flex gap-1 rounded-lg border border-border p-1"
        aria-label="Theme"
      >
        {themeOptions.map((option) => {
          const isActive =
            mounted && theme === option.value;

          return (
            <button
              key={option.value}
              type="button"
              onClick={() => setTheme(option.value)}
              aria-pressed={isActive}
              className={`rounded-md px-3 py-1.5 text-sm transition-colors ${
                isActive
                  ? "bg-foreground text-background"
                  : "text-muted-foreground hover:bg-foreground/10 hover:text-foreground"
              }`}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
