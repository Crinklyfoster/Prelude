interface Props {
  preview: string;
  score: number;
}

export function SourceCard({
  preview,
  score,
}: Props) {
  return (
    <div className="mt-3 rounded-lg border bg-muted/40 p-3">
      <div className="text-xs text-muted-foreground">
        Similarity {(1 - score).toFixed(2)}
      </div>

      <p className="mt-2 text-sm">{preview}</p>
    </div>
  );
}

