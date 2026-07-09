import { useEffect, useRef, useState } from "react";
import type { FormEvent, InputHTMLAttributes } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { createBooking } from "../api/endpoints";
import { Button } from "../components/Button";
import { HoldTimer } from "../components/HoldTimer";
import { useCountdown } from "../hooks/useCountdown";
import { formatMoney } from "../lib/format";
import { newIdempotencyKey } from "../lib/session";
import { useSelection } from "../store/selection";

// --- Маски ввода карты ---
function maskCardNumber(v: string): string {
  const digits = v.replace(/\D/g, "").slice(0, 16);
  return digits.replace(/(.{4})/g, "$1 ").trim(); // 1111 1111 1111 1111
}
function maskExpiry(v: string): string {
  const digits = v.replace(/\D/g, "").slice(0, 4);
  return digits.length <= 2 ? digits : `${digits.slice(0, 2)}/${digits.slice(2)}`;
}
function maskCvv(v: string): string {
  return v.replace(/\D/g, "").slice(0, 4);
}

function Field({
  label,
  ...props
}: { label: string } & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[11px] font-semibold uppercase tracking-[0.15em] text-muted">
        {label}
      </span>
      <input
        {...props}
        className="border border-line bg-white px-4 py-3 text-sm outline-none transition-colors focus:border-terracotta"
      />
    </label>
  );
}

export default function CheckoutPage() {
  const navigate = useNavigate();
  const hold = useSelection((s) => s.hold);
  const reset = useSelection((s) => s.reset);

  const idempotencyKey = useRef(newIdempotencyKey()).current;
  const done = useRef(false); // защита от «сторожа» после успешной оплаты
  const remaining = useCountdown(hold?.expires_at ?? null);
  const expired = hold != null && remaining === 0;

  const [form, setForm] = useState({
    email: "",
    number: "",
    expiry: "",
    cvv: "",
    holder: "",
  });
  const [error, setError] = useState<string | null>(null);

  // Нет активного холда — возвращаем на главную (но не после успешной оплаты).
  useEffect(() => {
    if (!hold && !done.current) navigate("/", { replace: true });
  }, [hold, navigate]);

  const booking = useMutation({
    mutationFn: () =>
      createBooking({
        hold_id: hold!.id,
        email: form.email,
        payment: {
          number: form.number,
          expiry: form.expiry,
          cvv: form.cvv,
          holder: form.holder,
        },
        idempotency_key: idempotencyKey,
      }),
    onSuccess: (b) => {
      done.current = true;
      reset();
      navigate(`/booking/${b.reference}`);
    },
    onError: (err) => {
      if (err instanceof ApiError && err.status === 402) {
        setError("Your card was declined. Please try a different card.");
      } else if (err instanceof ApiError && err.status === 409) {
        setError("Your hold expired. Please pick your seats again.");
      } else {
        setError("Payment failed. Please check your details and try again.");
      }
    },
  });

  if (!hold) return null;

  if (expired) {
    return (
      <div className="mx-auto grid min-h-screen max-w-md place-items-center px-6 text-center">
        <div>
          <h1 className="font-display text-3xl">Your hold expired</h1>
          <p className="mt-3 text-muted">
            The seats were released back for sale. No worries — pick them again.
          </p>
          <Button className="mt-8" onClick={() => navigate(`/events/${hold.event_id}`)}>
            Back to seats
          </Button>
        </div>
      </div>
    );
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    booking.mutate();
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-4xl">Checkout</h1>
        <HoldTimer expiresAt={hold.expires_at} />
      </div>

      <div className="grid gap-10 lg:grid-cols-[1fr_320px]">
        {/* Форма */}
        <form onSubmit={submit} className="flex flex-col gap-5">
          <Field
            label="Email"
            type="email"
            required
            placeholder="you@example.com"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <Field
            label="Card number"
            required
            inputMode="numeric"
            placeholder="4242 4242 4242 4242"
            value={form.number}
            onChange={(e) => setForm({ ...form, number: maskCardNumber(e.target.value) })}
          />
          <div className="grid grid-cols-2 gap-5">
            <Field
              label="Expiry (MM/YY)"
              required
              inputMode="numeric"
              placeholder="12/30"
              value={form.expiry}
              onChange={(e) => setForm({ ...form, expiry: maskExpiry(e.target.value) })}
            />
            <Field
              label="CVV"
              required
              inputMode="numeric"
              placeholder="123"
              value={form.cvv}
              onChange={(e) => setForm({ ...form, cvv: maskCvv(e.target.value) })}
            />
          </div>
          <Field
            label="Name on card"
            required
            placeholder="Alex Fan"
            value={form.holder}
            onChange={(e) => setForm({ ...form, holder: e.target.value })}
          />

          <p className="text-xs text-muted">
            Demo payment — use 4242 4242 4242 4242. Try 4000 0000 0000 0002 to see a
            decline.
          </p>

          {error && (
            <p className="border border-terracotta/40 bg-terracotta/10 px-4 py-3 text-sm text-terracotta-dark">
              {error}
            </p>
          )}

          <Button type="submit" disabled={booking.isPending} className="mt-2 w-full">
            {booking.isPending ? "Processing…" : `Pay ${formatMoney(hold.total_cents)}`}
          </Button>
        </form>

        {/* Сводка */}
        <aside className="h-fit border border-line bg-surface/40 p-6">
          <h2 className="mb-4 text-[11px] font-semibold uppercase tracking-[0.2em] text-muted">
            Your seats
          </h2>
          <ul className="flex flex-col gap-2">
            {hold.seats.map((s) => (
              <li key={s.id} className="flex justify-between text-sm">
                <span>
                  {s.zone_name} · {s.row}
                  {s.number}
                </span>
                <span>{formatMoney(s.price_cents)}</span>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex justify-between border-t border-line pt-4">
            <span className="text-sm text-muted">Total</span>
            <span className="font-display text-xl">
              {formatMoney(hold.total_cents)}
            </span>
          </div>
        </aside>
      </div>
    </div>
  );
}
