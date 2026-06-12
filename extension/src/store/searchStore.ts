import { create } from "zustand";

import type { Lead } from "../lib/types";

type SearchState = {
  jobId: string | null;
  liveLeads: Lead[];
  error: string | null;
  status: "idle" | "queued" | "running" | "completed" | "failed";
  setJob: (jobId: string, status: SearchState["status"]) => void;
  addLead: (lead: Lead) => void;
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
  setStatus: (status) => set({ status }),
  setError: (error) => set({ error })
}));
