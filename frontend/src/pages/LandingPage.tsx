import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import type { Variants } from "framer-motion";
import { Link } from "react-router-dom";

import { getTour } from "../api/endpoints";
import { Reveal } from "../components/Reveal";
import { formatDate, formatTime } from "../lib/format";

const list: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06, delayChildren: 0.25 } },
};
const item: Variants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

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
      <header className="mx-auto flex max-w-5xl flex-col items-center px-6 pt-20 pb-16 text-center sm:pt-24">
        <Reveal delay={0.05}>
          <p className="mb-6 text-xs font-semibold uppercase tracking-[0.35em] text-muted">
            World Tour{" "}
            {new Date(tour.events[0]?.starts_at ?? Date.now()).getFullYear()}
          </p>
        </Reveal>
        <Reveal delay={0.12}>
          <h1 className="font-display text-[clamp(3.5rem,15vw,11rem)] font-bold leading-[0.9] tracking-tight">
            {tour.artist}
          </h1>
        </Reveal>
        <Reveal delay={0.22}>
          <p className="mt-4 font-display text-3xl italic text-terracotta sm:text-4xl">
            {tour.title}
          </p>
        </Reveal>
        <Reveal delay={0.32}>
          <p className="mt-8 max-w-md text-sm leading-relaxed text-muted">
            {tour.description}
          </p>
        </Reveal>
      </header>

      {/* Tour dates */}
      <section className="mx-auto max-w-3xl px-6 pb-24">
        <h2 className="mb-8 border-b border-line pb-3 text-xs font-semibold uppercase tracking-[0.25em] text-muted">
          Tour dates
        </h2>
        <motion.ul
          variants={list}
          initial="hidden"
          animate="show"
          className="flex flex-col"
        >
          {tour.events.map((ev) => (
            <motion.li key={ev.id} variants={item}>
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
                <span className="ml-6 text-xs font-semibold uppercase tracking-[0.2em] text-terracotta transition-transform group-hover:translate-x-1">
                  Seats →
                </span>
              </Link>
            </motion.li>
          ))}
        </motion.ul>
      </section>
    </div>
  );
}
