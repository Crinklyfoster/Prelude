type Props = {
  title: string;
  value: number | string;
  accent?: "green" | "yellow" | "red" | "blue";
};

const accentMap: Record<NonNullable<Props["accent"]>, string> = {
  green:
    "border-l-emerald-500 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400",
  yellow:
    "border-l-amber-500 bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400",
  red: "border-l-red-500 bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-400",
  blue: "border-l-blue-500 bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-400",
};

export default function StatCard({ title, value, accent }: Props) {
  const accentClass = accent ? accentMap[accent] : "";

  return (
    <div
      className={`rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm transition-shadow hover:shadow-md border-l-4 ${accentClass}`}
    >
      <p className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
        {title}
      </p>
      <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
        {value}
      </p>
    </div>
  );
}
