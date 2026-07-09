import { create } from "zustand";

import type { Hold } from "../api/types";

interface SelectionState {
  eventId: number | null;
  selected: number[]; // id выбранных мест (до создания холда)
  hold: Hold | null;

  setEvent: (id: number) => void;
  toggleSeat: (id: number) => void;
  clearSelection: () => void;
  setHold: (hold: Hold | null) => void;
  reset: () => void;
}

// Выбор мест и активный холд. session_token — в localStorage (lib/session).
export const useSelection = create<SelectionState>((set) => ({
  eventId: null,
  selected: [],
  hold: null,

  setEvent: (id) =>
    set((s) => (s.eventId === id ? s : { eventId: id, selected: [], hold: null })),

  toggleSeat: (id) =>
    set((s) => ({
      selected: s.selected.includes(id)
        ? s.selected.filter((x) => x !== id)
        : [...s.selected, id],
    })),

  clearSelection: () => set({ selected: [] }),
  setHold: (hold) => set({ hold }),
  reset: () => set({ selected: [], hold: null }),
}));
