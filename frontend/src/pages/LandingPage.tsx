import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getTour } from "../api/endpoints";
import { formatDate, formatTime } from "../lib/format";

export default function LandingPage() {
  const { data: tour, isLoading, isError } = useQuery({
    queryKey: ["tour"],
    queryFn: getTour,
  });

  if (isLoading)
    return <div className="grid min-h-screen place-items-center text-muted">Loading…</div>;
  if (isError || !tour)
    return (
      <div className="grid min-h-screen place-items-center text-muted">
        Could not load the tour.
      </div>
    );

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <header className="mx-auto flex max-w-5xl flex-col items-center px-6 pt-24 pb-16 text-center">
        <p className="mb-6 text-xs font-semibold uppercase tracking-[0.35em] text-muted">
          World Tour {new Date(tour.events[0]?.starts_at ?? Date.now()).getFullYear()}
        </p>
        <h1 className="font-display text-[clamp(3.5rem,15vw,11rem)] font-bold leading-[0.9] tracking-tight">
          {tour.artist}
        </h1>
        <p className="mt-4 font-display text-3xl italic text-terracotta sm:text-4xl">
          {tour.title}
        </p>
        <p className="mt-8 max-w-md text-sm leading-relaxed text-muted">
          {tour.description}
        </p>
      </header>

      {/* Tour dates */}
      <section className="mx-auto max-w-3xl px-6 pb-24">
        <h2 className="mb-8 border-b border-line pb-3 text-xs font-semibold uppercase tracking-[0.25em] text-muted">
          Tour dates
        </h2>
        <ul className="flex flex-col">
          {tour.events.map((ev) => (
            <li key={ev.id}>
              <Link
                to={`/events/${ev.id}`}
                className="group flex items-center justify-between border-b border-line py-6 transition-colors hover:bg-surface/50"
              >
                <div className="flex-1">
                  <div className="font-display text-2xl">{ev.city}</div>
                  <div className="text-sm text-muted">{ev.venue}</div>
                </div>
                <div className="hidden text-right text-sm text-muted sm:block">
                  <div>{formatDate(ev.starts_at)}</div>
                  <div>{formatTime(ev.starts_at)}</div>
                </div>
                <span className="ml-8 text-xs font-semibold uppercase tracking-[0.2em] text-terracotta transition-transform group-hover:translate-x-1">
                  Select seats →
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
