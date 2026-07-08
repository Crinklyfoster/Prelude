import { ButtonHTMLAttributes } from "react";
import clsx from "clsx";

export function Button({
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={clsx(
        "rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700 disabled:opacity-50",
        className
      )}
      {...props}
    />
  );
}

