import { api, API_BASE } from "./client";
import type { Booking, EventDetail, Hold, SeatMap, Tour } from "./types";

export const getTour = () => api<Tour>("/api/tour");
export const getEvent = (id: number) => api<EventDetail>(`/api/events/${id}`);
export const getSeatMap = (id: number) => api<SeatMap>(`/api/events/${id}/seats`);

export const createHold = (body: {
  event_id: number;
  seat_ids: number[];
  session_token: string;
}) => api<Hold>("/api/holds", { method: "POST", body: JSON.stringify(body) });

export const getHold = (id: number) => api<Hold>(`/api/holds/${id}`);
export const releaseHold = (id: number) =>
  api<void>(`/api/holds/${id}`, { method: "DELETE" });

export const createBooking = (body: {
  hold_id: number;
  email: string;
  payment: { number: string; expiry: string; cvv: string; holder: string };
  idempotency_key: string;
}) => api<Booking>("/api/bookings", { method: "POST", body: JSON.stringify(body) });

export const getBooking = (reference: string) =>
  api<Booking>(`/api/bookings/${reference}`);

export const ticketPdfUrl = (reference: string, code: string) =>
  `${API_BASE}/api/bookings/${reference}/tickets/${code}`;
