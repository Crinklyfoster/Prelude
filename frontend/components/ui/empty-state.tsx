import { ReactNode } from "react";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
}

export function EmptyState({
  icon,
  title,
  description,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="mb-4 text-5xl">{icon}</div>

      <h2 className="text-xl font-semibold">{title}</h2>

      <p className="mt-2 text-gray-500">{description}</p>
    </div>
  );
}

