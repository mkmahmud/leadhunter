import { create } from "zustand";

import type { Lead } from "../lib/types";

type SearchState = {
  jobId: string | null;
  liveLeads: Lead[];
  error: string | null;
  status: "idle" | "queued" | "running" | "completed" | "failed";
  setJob: (jobId: string, status: SearchState["status"]) => void;
  addLead: (lead: Lead) => void;
  addLeads: (leads: Lead[]) => void;
  setStatus: (status: SearchState["status"]) => void;
  setError: (error: string | null) => void;
};

export const useSearchStore = create<SearchState>((set) => ({
  jobId: null,
  liveLeads: [],
  error: null,
  status: "idle",
  setJob: (jobId, status) => set({ jobId, status, liveLeads: [], error: null }),
  addLead: (lead) => set((state) => ({ liveLeads: [lead, ...state.liveLeads.filter((item) => item.id !== lead.id)] })),
  addLeads: (leads) =>
    set((state) => {
      const merged = new Map([...leads, ...state.liveLeads].map((lead) => [lead.id, lead]));
      return { liveLeads: [...merged.values()] };
    }),
  setStatus: (status) => set({ status }),
  setError: (error) => set({ error })
}));
