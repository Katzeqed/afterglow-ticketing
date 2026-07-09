import { useRef, useState } from "react";
import type { MouseEvent } from "react";
import { TransformComponent, TransformWrapper } from "react-zoom-pan-pinch";

import type { ZoneWithSeats } from "../api/types";
import { formatMoney } from "../lib/format";

const R = 9; // радиус места

interface FlatSeat {
  id: number;
  x: number;
  y: number;
  row: string;
  number: number;
  status: string;
  color: string;
  zoneName: string;
  price: number;
}

interface HoverState {
  seat: FlatSeat;
  left: number;
  top: number;
}

export function SeatMap({
  zones,
  selected,
  onToggle,
}: {
  zones: ZoneWithSeats[];
  selected: number[];
  onToggle: (seatId: number) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState<HoverState | null>(null);

  const seats: FlatSeat[] = zones.flatMap((z) =>
    z.seats.map((s) => ({
      id: s.id,
      x: s.x,
      y: s.y,
      row: s.row,
      number: s.number,
      status: s.status,
      color: z.color,
      zoneName: z.name,
      price: z.price_cents,
    })),
  );

  const xs = seats.map((s) => s.x);
  const ys = seats.map((s) => s.y);
  const minX = Math.min(...xs) - 24;
  const maxX = Math.max(...xs) + 24;
  const minY = Math.min(...ys) - 40;
  const maxY = Math.max(...ys) + 24;
  const width = maxX - minX;
  const height = maxY - minY;
  const selectedSet = new Set(selected);

  function showTooltip(seat: FlatSeat, e: MouseEvent) {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    setHover({
      seat,
      left: e.clientX - rect.left,
      top: e.clientY - rect.top,
    });
  }

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="w-full overflow-hidden border border-line bg-surface/40">
        <TransformWrapper minScale={0.6} maxScale={5} centerOnInit>
          <TransformComponent
            wrapperStyle={{ width: "100%", height: "62vh" }}
            contentStyle={{ width: "100%" }}
          >
          <svg viewBox={`${minX} ${minY} ${width} ${height}`} className="w-full">
            {/* Сцена */}
            <rect
              x={minX + width * 0.28}
              y={minY + 6}
              width={width * 0.44}
              height={8}
              rx={4}
              fill="#211e1a"
              opacity={0.18}
            />
            <text
              x={minX + width * 0.5}
              y={minY + 30}
              textAnchor="middle"
              fontSize={14}
              fill="#6b635a"
              letterSpacing={6}
            >
              STAGE
            </text>

            {seats.map((s) => {
              const isSelected = selectedSet.has(s.id);
              const clickable = s.status === "available";

              let fill = s.color;
              let fillOpacity = 0.9;
              let stroke = "none";
              let strokeWidth = 0;

              if (s.status === "held") {
                fill = "#d69a4c";
                fillOpacity = 0.4;
              } else if (s.status === "booked") {
                fill = "#c9c0b2";
                fillOpacity = 0.55;
              }
              if (isSelected) {
                stroke = "#211e1a";
                strokeWidth = 2.5;
                fillOpacity = 1;
              }

              return (
                <circle
                  key={s.id}
                  cx={s.x}
                  cy={s.y}
                  r={isSelected ? R + 1 : R}
                  fill={fill}
                  fillOpacity={fillOpacity}
                  stroke={stroke}
                  strokeWidth={strokeWidth}
                  aria-label={`${s.zoneName}, row ${s.row}, seat ${s.number}, ${s.status}`}
                  style={{
                    cursor: clickable ? "pointer" : "default",
                    transition: "r 0.12s ease, fill-opacity 0.15s ease",
                  }}
                  onMouseMove={(e) => showTooltip(s, e)}
                  onMouseLeave={() => setHover(null)}
                  onClick={() => clickable && onToggle(s.id)}
                />
              );
            })}
          </svg>
          </TransformComponent>
        </TransformWrapper>
      </div>

      {/* Плашка при наведении (переворачивается вниз у верхнего края) */}
      {hover && (
        <div
          className={
            "pointer-events-none absolute z-10 -translate-x-1/2 rounded-sm border border-line bg-paper px-3 py-2 text-xs shadow-lg " +
            (hover.top < 80 ? "translate-y-0" : "-translate-y-full")
          }
          style={{ left: hover.left, top: hover.top < 80 ? hover.top + 16 : hover.top - 12 }}
        >
          <div className="font-semibold text-ink">{hover.seat.zoneName}</div>
          <div className="text-muted">
            Row {hover.seat.row} · Seat {hover.seat.number}
          </div>
          <div className="mt-0.5 flex items-center gap-2">
            <span className="font-medium text-ink">
              {formatMoney(hover.seat.price)}
            </span>
            {hover.seat.status !== "available" && (
              <span className="uppercase tracking-wide text-[10px] text-terracotta">
                {hover.seat.status === "booked" ? "Sold" : "On hold"}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
