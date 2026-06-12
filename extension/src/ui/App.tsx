import { useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Download, FileJson, RefreshCw, ScanSearch } from "lucide-react";

import { createJobEvents, downloadExport, getLeads, ingestCapturedLeads } from "../lib/api";
import type { CapturedLead } from "../lib/types";
import { useSearchStore } from "../store/searchStore";
import { Button, IconButton } from "./primitives";
import { ResultsTable } from "./ResultsTable";
import { SearchForm } from "./SearchForm";

export function App() {
  const { refetch } = useQuery({ queryKey: ["leads"], queryFn: getLeads, enabled: false });
  const jobId = useSearchStore((state) => state.jobId);
  const liveLeads = useSearchStore((state) => state.liveLeads);
  const addLead = useSearchStore((state) => state.addLead);
  const addLeads = useSearchStore((state) => state.addLeads);
  const status = useSearchStore((state) => state.status);
  const error = useSearchStore((state) => state.error);
  const setStatus = useSearchStore((state) => state.setStatus);
  const setError = useSearchStore((state) => state.setError);

  useEffect(() => {
    if (!jobId) return;
    const events = createJobEvents(jobId);
    events.onmessage = (message) => {
      const payload = JSON.parse(message.data) as { type: string; lead?: import("../lib/types").Lead; error?: string };
      if (payload.type === "lead" && payload.lead) addLead(payload.lead);
      if (payload.type === "completed") {
        setStatus("completed");
        void refetch();
        events.close();
      }
      if (payload.type === "failed") {
        setStatus("failed");
        setError(payload.error ?? "Search failed");
      }
    };
    return () => events.close();
  }, [addLead, jobId, refetch, setError, setStatus]);

  const leads = useMemo(() => [...liveLeads].sort((a, b) => b.lead_score - a.lead_score), [liveLeads]);

  async function captureCurrentPage() {
    try {
      setError(null);
      setStatus("running");
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab.id || !tab.url?.startsWith("http")) {
        throw new Error("Open a public http/https page first, then capture it.");
      }
      const response = await requestCurrentPageCapture(tab.id);
      const captured = ((response as { items?: CapturedLead[] } | undefined)?.items ?? []).filter((item) => item.post_content);
      if (!captured.length) {
        throw new Error("No visible intent posts found on this page. Try opening a search/results page with posts visible.");
      }
      const result = await ingestCapturedLeads(captured, 0);
      addLeads(result.items);
      setStatus("completed");
      if (!result.ingested) {
        setError(`Captured ${captured.length} items, but all were skipped by scoring/deduplication.`);
      }
    } catch (error) {
      setStatus("failed");
      setError(error instanceof Error ? error.message : "Current page capture failed");
    }
  }

  async function requestCurrentPageCapture(tabId: number) {
    try {
      return await chrome.tabs.sendMessage(tabId, { type: "SCRAPE_VISIBLE_LEADS" });
    } catch {
      await chrome.scripting.executeScript({ target: { tabId }, files: ["assets/content.js"] });
      return chrome.tabs.sendMessage(tabId, { type: "SCRAPE_VISIBLE_LEADS" });
    }
  }

  return (
    <main className="grid min-h-screen grid-cols-[380px_1fr] bg-background text-foreground">
      <aside className="h-screen overflow-auto border-r border-border bg-panel">
        <div className="border-b border-border px-4 py-4">
          <h1 className="text-lg font-semibold">Founder Intent Leads</h1>
          <p className="mt-1 text-sm text-muted">Capture visible public posts from the page you opened.</p>
        </div>
        <SearchForm />
      </aside>

      <section className="min-w-0">
        <header className="flex items-center justify-between border-b border-border bg-panel px-4 py-3">
          <div>
            <div className="text-sm font-semibold">{leads.length.toLocaleString()} leads</div>
            <div className="text-xs capitalize text-muted">Status: {status}</div>
            {error && <div className="mt-1 max-w-[560px] text-xs font-medium text-red-700">{error}</div>}
            {!leads.length && !error && <div className="mt-1 text-xs text-muted">Run a search to populate results.</div>}
          </div>
          <div className="flex gap-2">
            <Button title="Capture visible leads from current tab" onClick={() => void captureCurrentPage()}>
              <ScanSearch className="size-4" />
              Capture Page
            </Button>
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
