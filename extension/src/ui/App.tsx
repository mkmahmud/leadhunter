import { useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Download, FileJson, RefreshCw } from "lucide-react";

import { createJobEvents, downloadExport, getLeads } from "../lib/api";
import { useSearchStore } from "../store/searchStore";
import { IconButton } from "./primitives";
import { ResultsTable } from "./ResultsTable";
import { SearchForm } from "./SearchForm";

export function App() {
  const { data, refetch } = useQuery({ queryKey: ["leads"], queryFn: getLeads });
  const jobId = useSearchStore((state) => state.jobId);
  const liveLeads = useSearchStore((state) => state.liveLeads);
  const addLead = useSearchStore((state) => state.addLead);
  const status = useSearchStore((state) => state.status);
  const setStatus = useSearchStore((state) => state.setStatus);

  useEffect(() => {
    if (!jobId) return;
    const events = createJobEvents(jobId);
    events.onmessage = (message) => {
      const payload = JSON.parse(message.data) as { type: string; lead?: import("../lib/types").Lead };
      if (payload.type === "lead" && payload.lead) addLead(payload.lead);
      if (payload.type === "completed") {
        setStatus("completed");
        void refetch();
        events.close();
      }
      if (payload.type === "failed") setStatus("failed");
    };
    return () => events.close();
  }, [addLead, jobId, refetch, setStatus]);

  const leads = useMemo(() => {
    const persisted = data?.items ?? [];
    const merged = new Map([...liveLeads, ...persisted].map((lead) => [lead.id, lead]));
    return [...merged.values()].sort((a, b) => b.lead_score - a.lead_score);
  }, [data?.items, liveLeads]);

  return (
    <main className="grid min-h-screen grid-cols-[380px_1fr] bg-background text-foreground">
      <aside className="h-screen overflow-auto border-r border-border bg-panel">
        <div className="border-b border-border px-4 py-4">
          <h1 className="text-lg font-semibold">Founder Intent Leads</h1>
          <p className="mt-1 text-sm text-muted">Search public buying signals from founders and decision makers.</p>
        </div>
        <SearchForm />
      </aside>

      <section className="min-w-0">
        <header className="flex items-center justify-between border-b border-border bg-panel px-4 py-3">
          <div>
            <div className="text-sm font-semibold">{leads.length.toLocaleString()} leads</div>
            <div className="text-xs capitalize text-muted">Status: {status}</div>
          </div>
          <div className="flex gap-2">
            <IconButton title="Refresh leads" onClick={() => void refetch()}>
              <RefreshCw className="size-4" />
            </IconButton>
            <IconButton title="Export CSV" onClick={() => void downloadExport("csv")}>
              <Download className="size-4" />
            </IconButton>
            <IconButton title="Export JSON" onClick={() => void downloadExport("json")}>
              <FileJson className="size-4" />
            </IconButton>
          </div>
        </header>
        <ResultsTable leads={leads} />
      </section>
    </main>
  );
}
