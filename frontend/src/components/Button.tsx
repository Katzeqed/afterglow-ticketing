import type { ButtonHTMLAttributes } from "react";

export function Button({
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className={
        "inline-flex items-center justify-center bg-ink px-8 py-4 text-xs font-semibold " +
        "uppercase tracking-[0.22em] text-paper transition-colors duration-200 " +
        "hover:bg-terracotta disabled:cursor-not-allowed disabled:opacity-40 " +
        className
      }
    />
  );
}
