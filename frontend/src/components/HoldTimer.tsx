import { useCountdown } from "../hooks/useCountdown";
import { formatClock } from "../lib/format";

export function HoldTimer({
  expiresAt,
  onExpire,
}: {
  expiresAt: string;
  onExpire?: () => void;
}) {
  const remaining = useCountdown(expiresAt);
  const urgent = remaining <= 60;

  if (remaining === 0) {
    // Вызываем колбэк один раз, когда дошли до нуля.
    onExpire?.();
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-muted">Seats held for</span>
      <span
        className={
          "font-display text-lg tabular-nums " +
          (urgent ? "text-terracotta" : "text-ink")
        }
      >
        {formatClock(remaining)}
      </span>
    </div>
  );
}
