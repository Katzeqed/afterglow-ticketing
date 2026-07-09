import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Link, useParams } from "react-router-dom";

import { getBooking, ticketPdfUrl } from "../api/endpoints";
import { Reveal } from "../components/Reveal";
import { formatDate, formatMoney, formatTime } from "../lib/format";

export default function ConfirmationPage() {
  const { reference } = useParams();

  const { data: booking, isLoading, isError } = useQuery({
    queryKey: ["booking", reference],
    queryFn: () => getBooking(reference!),
    enabled: !!reference,
  });

  if (isLoading)
    return <div className="grid min-h-screen place-items-center text-muted">Loading…</div>;
  if (isError || !booking)
    return (
      <div className="grid min-h-screen place-items-center text-muted">
        Booking not found.
      </div>
    );

  return (
    <div className="mx-auto max-w-2xl px-6 py-16 text-center">
      <motion.div
        initial={{ scale: 0.6, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 18 }}
        className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-full border border-terracotta text-terracotta"
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </motion.div>

      <Reveal delay={0.15}>
        <h1 className="font-display text-4xl">You're going</h1>
        <p className="mt-3 text-sm text-muted">
          Confirmation sent to <span className="text-ink">{booking.email}</span>. Booking{" "}
          <span className="font-mono">{booking.reference}</span>.
        </p>

        <div className="mt-4 text-sm text-muted">
          {booking.city} · {booking.venue} · {formatDate(booking.starts_at)} ·{" "}
          {formatTime(booking.starts_at)}
        </div>
      </Reveal>

      {/* Билеты */}
      <ul className="mt-10 flex flex-col gap-3 text-left">
        {booking.tickets.map((t) => (
          <li
            key={t.code}
            className="flex items-center justify-between border border-line bg-surface/40 p-4"
          >
            <div>
              <div className="text-sm font-semibold">
                {t.zone_name} · Row {t.row}, Seat {t.number}
              </div>
              <div className="font-mono text-xs text-muted">{t.code}</div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm">{formatMoney(t.price_cents)}</span>
              <a
                href={ticketPdfUrl(booking.reference, t.code)}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-semibold uppercase tracking-[0.15em] text-terracotta hover:underline"
              >
                PDF ↓
              </a>
            </div>
          </li>
        ))}
      </ul>

      <div className="mt-6 flex items-center justify-between border-t border-line pt-4 text-left">
        <span className="text-sm text-muted">Total paid</span>
        <span className="font-display text-2xl">{formatMoney(booking.total_cents)}</span>
      </div>

      <Link
        to="/"
        className="mt-10 inline-block text-xs font-semibold uppercase tracking-[0.2em] text-muted hover:text-ink"
      >
        ← Back to tour
      </Link>
    </div>
  );
}
