"use client";

import { useState } from "react";

import { Source } from "@/types/chat";

interface SourceCardProps {
  source: Source;
  index: number;
}

const COLLAPSED_PREVIEW_LENGTH = 80;

export default function SourceCard({
  source,
  index,
}: SourceCardProps) {
  const [expanded, setExpanded] = useState(false);
  const canExpand =
    source.preview.length > COLLAPSED_PREVIEW_LENGTH;
  const preview =
    expanded || !canExpand
      ? source.preview
      : `${source.preview
          .slice(0, COLLAPSED_PREVIEW_LENGTH)
          .trimEnd()}...`;

  return (
    <div className="mt-2 rounded-lg border p-3">
      <div className="flex justify-between gap-4">
        <span>Source {index + 1}</span>

        <span className="text-right">
          Confidence: {(source.score * 100).toFixed(1)}%
        </span>
      </div>

      <p className="mt-2 text-sm">{preview}</p>

      {canExpand && (
        <button
          type="button"
          onClick={() => setExpanded((current) => !current)}
          className="mt-2 text-sm underline"
          aria-expanded={expanded}
        >
          {expanded ? "Show Less" : "Show More"}
        </button>
      )}
    </div>
  );
}
