import { create } from "zustand";

import type { Lead } from "../lib/types";

type SearchState = {
  jobId: string | null;
  liveLeads: Lead[];
  status: "idle" | "queued" | "running" | "completed" | "failed";
  setJob: (jobId: string, status: SearchState["status"]) => void;
  addLead: (lead: Lead) => void;
  setStatus: (status: SearchState["status"]) => void;
};

export const useSearchStore = create<SearchState>((set) => ({
  jobId: null,
  liveLeads: [],
  status: "idle",
  setJob: (jobId, status) => set({ jobId, status, liveLeads: [] }),
  addLead: (lead) => set((state) => ({ liveLeads: [lead, ...state.liveLeads.filter((item) => item.id !== lead.id)] })),
  setStatus: (status) => set({ status })
}));
