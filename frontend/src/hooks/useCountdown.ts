import { useEffect, useState } from "react";

// Секунды до expiresAt, тикает раз в секунду. 0 — если истёк/нет холда.
export function useCountdown(expiresAt: string | null | undefined): number {
  const [remaining, setRemaining] = useState(0);

  useEffect(() => {
    if (!expiresAt) {
      setRemaining(0);
      return;
    }
    const target = new Date(expiresAt).getTime();
    const tick = () =>
      setRemaining(Math.max(0, Math.round((target - Date.now()) / 1000)));
    tick();
    const iv = setInterval(tick, 1000);
    return () => clearInterval(iv);
  }, [expiresAt]);

  return remaining;
}
