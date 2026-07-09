import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";

import { createHold, getEvent, getSeatMap } from "../api/endpoints";
import { ApiError } from "../api/client";
import { Button } from "../components/Button";
import { SeatMap } from "../components/SeatMap";
import { ZoneLegend } from "../components/ZoneLegend";
import { formatDate, formatMoney, formatTime } from "../lib/format";
import { getSessionToken } from "../lib/session";
import { useSelection } from "../store/selection";

const MAX_SEATS = 8;

export default function SeatMapPage() {
  const { id } = useParams();
  const eventId = Number(id);
  const navigate = useNavigate();

  const { selected, toggleSeat, setEvent, clearSelection, setHold } = useSelection();
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    setEvent(eventId);
  }, [eventId, setEvent]);

  const eventQuery = useQuery({
    queryKey: ["event", eventId],
    queryFn: () => getEvent(eventId),
  });
  const seatsQuery = useQuery({
    queryKey: ["seats", eventId],
    queryFn: () => getSeatMap(eventId),
    refetchInterval: 10_000, // видеть чужие холды
  });

  // Карта seatId -> цена/зона/место (для сводки).
  const seatIndex = useMemo(() => {
    const map = new Map<
      number,
      { price: number; zone: string; row: string; number: number }
    >();
    seatsQuery.data?.zones.forEach((z) =>
      z.seats.forEach((s) =>
        map.set(s.id, {
          price: z.price_cents,
          zone: z.name,
          row: s.row,
          number: s.number,
        }),
      ),
    );
    return map;
  }, [seatsQuery.data]);

  const total = selected.reduce((sum, sid) => sum + (seatIndex.get(sid)?.price ?? 0), 0);

  const holdMutation = useMutation({
    mutationFn: () =>
      createHold({
        event_id: eventId,
        seat_ids: selected,
        session_token: getSessionToken(),
      }),
    onSuccess: (hold) => {
      setHold(hold);
      navigate("/checkout");
    },
    onError: (err) => {
      if (err instanceof ApiError && err.status === 409) {
        setNotice("Some of your seats were just taken. Please pick again.");
        clearSelection();
        seatsQuery.refetch();
      } else {
        setNotice("Could not hold the seats. Please try again.");
      }
    },
  });

  function handleToggle(seatId: number) {
    setNotice(null);
    if (!selected.includes(seatId) && selected.length >= MAX_SEATS) {
      setNotice(`You can select up to ${MAX_SEATS} seats.`);
      return;
    }
    toggleSeat(seatId);
  }

  if (eventQuery.isLoading || seatsQuery.isLoading)
    return <div className="grid min-h-screen place-items-center text-muted">Loading…</div>;
  if (eventQuery.isError || !eventQuery.data || !seatsQuery.data)
    return (
      <div className="grid min-h-screen place-items-center text-muted">
        Could not load the event.
      </div>
    );

  const ev = eventQuery.data;

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <Link to="/" className="text-xs uppercase tracking-[0.2em] text-muted hover:text-ink">
        ← All dates
      </Link>

      <header className="mt-4 mb-6">
        <h1 className="font-display text-4xl">{ev.city}</h1>
        <p className="text-muted">
          {ev.venue} · {formatDate(ev.starts_at)} · {formatTime(ev.starts_at)}
        </p>
      </header>

      <div className="mb-4">
        <ZoneLegend zones={seatsQuery.data.zones} />
      </div>

      <p className="mb-3 text-xs text-muted">
        Scroll to zoom, drag to pan. Click a seat to select.
      </p>

      <SeatMap
        zones={seatsQuery.data.zones}
        selected={selected}
        onToggle={handleToggle}
      />

      {notice && (
        <p className="mt-4 border border-terracotta/40 bg-terracotta/10 px-4 py-3 text-sm text-terracotta-dark">
          {notice}
        </p>
      )}

      {/* Панель выбора */}
      <div className="sticky bottom-0 mt-6 flex flex-col gap-4 border-t border-line bg-paper/95 py-5 backdrop-blur sm:flex-row sm:items-center sm:justify-between">
        <div className="text-sm">
          {selected.length === 0 ? (
            <span className="text-muted">No seats selected</span>
          ) : (
            <span>
              <span className="font-semibold">{selected.length}</span> seat
              {selected.length > 1 ? "s" : ""} · {formatMoney(total)}
            </span>
          )}
        </div>
        <Button
          disabled={selected.length === 0 || holdMutation.isPending}
          onClick={() => holdMutation.mutate()}
        >
          {holdMutation.isPending ? "Holding…" : "Continue"}
        </Button>
      </div>
    </div>
  );
}
