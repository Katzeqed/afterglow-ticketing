// Типы ответов API (зеркалят Pydantic-схемы бэкенда).

export interface EventSummary {
  id: number;
  city: string;
  venue: string;
  starts_at: string;
  status: string;
}

export interface Tour {
  artist: string;
  title: string;
  description: string;
  events: EventSummary[];
}

export interface ZoneSummary {
  id: number;
  name: string;
  price_cents: number;
  color: string;
  display_order: number;
  total_seats: number;
  available_seats: number;
}

export interface EventDetail {
  id: number;
  city: string;
  venue: string;
  starts_at: string;
  status: string;
  currency: string;
  zones: ZoneSummary[];
}

export type SeatStatus = "available" | "held" | "booked";

export interface SeatOut {
  id: number;
  row: string;
  number: number;
  x: number;
  y: number;
  status: SeatStatus;
}

export interface ZoneWithSeats {
  id: number;
  name: string;
  price_cents: number;
  color: string;
  display_order: number;
  seats: SeatOut[];
}

export interface SeatMap {
  event_id: number;
  currency: string;
  zones: ZoneWithSeats[];
}

export interface HeldSeat {
  id: number;
  row: string;
  number: number;
  zone_name: string;
  price_cents: number;
}

export interface Hold {
  id: number;
  event_id: number;
  status: string;
  expires_at: string;
  seconds_remaining: number;
  total_cents: number;
  currency: string;
  seats: HeldSeat[];
}

export interface TicketOut {
  code: string;
  seat_id: number;
  row: string;
  number: number;
  zone_name: string;
  price_cents: number;
}

export interface Booking {
  reference: string;
  status: string;
  email: string;
  event_id: number;
  city: string;
  venue: string;
  starts_at: string;
  total_cents: number;
  currency: string;
  tickets: TicketOut[];
}
