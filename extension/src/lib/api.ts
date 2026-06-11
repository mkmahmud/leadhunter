import type { Lead, SearchPayload } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";
const CSRF_TOKEN = import.meta.env.VITE_CSRF_TOKEN ?? "local-csrf-token";

export async function token(): Promise<string> {
  const stored = await chrome.storage.local.get("accessToken");
  if (stored.accessToken) return stored.accessToken as string;
  const response = await fetch(`${API_BASE}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": CSRF_TOKEN },
    body: JSON.stringify({ username: "local-admin", password: "local-dev" })
  });
  const data = (await response.json()) as { access_token: string };
  await chrome.storage.local.set({ accessToken: data.access_token });
  return data.access_token;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const accessToken = await token();
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
      "X-CSRF-Token": CSRF_TOKEN,
      ...init?.headers
    }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return (await response.json()) as T;
}

export async function startSearch(payload: SearchPayload) {
  return request<{ job_id: string; status: string }>("/search", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function getLeads() {
  return request<{ items: Lead[]; total: number; page: number; page_size: number }>("/leads?page_size=100");
}

export function createJobEvents(jobId: string) {
  return new EventSource(`${API_BASE}/search/${jobId}/events`);
}

export function exportUrl(format: "csv" | "json") {
  return `${API_BASE}/export/${format}`;
}

export async function downloadExport(format: "csv" | "json") {
  const accessToken = await token();
  const response = await fetch(exportUrl(format), {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  if (!response.ok) throw new Error(await response.text());
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const extension = format === "csv" ? "csv" : "json";
  await chrome.downloads.download({ url, filename: `founder-intent-leads.${extension}`, saveAs: true });
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}
