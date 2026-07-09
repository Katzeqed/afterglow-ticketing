import type { ZoneWithSeats } from "../api/types";
import { formatMoney } from "../lib/format";

export function ZoneLegend({ zones }: { zones: ZoneWithSeats[] }) {
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-3">
      {zones.map((z) => {
        const available = z.seats.filter((s) => s.status === "available").length;
        return (
          <div key={z.id} className="flex items-center gap-2">
            <span
              className="inline-block h-3 w-3 rounded-full"
              style={{ backgroundColor: z.color }}
            />
            <span className="text-sm font-medium">{z.name}</span>
            <span className="text-sm text-muted">
              {formatMoney(z.price_cents)} · {available} left
            </span>
          </div>
        );
      })}
    </div>
  );
}
