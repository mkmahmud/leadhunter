import { ExternalLink } from "lucide-react";

import type { Lead } from "../lib/types";
import { IconButton } from "./primitives";

function scoreClass(score: number) {
  if (score >= 80) return "bg-emerald-100 text-emerald-800";
  if (score >= 50) return "bg-amber-100 text-amber-800";
  return "bg-slate-100 text-slate-700";
}

export function ResultsTable({ leads }: { leads: Lead[] }) {
  return (
    <div className="overflow-auto">
      <table className="w-full min-w-[760px] border-collapse text-left text-sm">
        <thead className="sticky top-0 bg-background text-xs uppercase text-muted">
          <tr>
            {["Name", "Role", "Company", "Website", "Email", "Platform", "Score", "Date", ""].map((header) => (
              <th key={header} className="border-b border-border px-3 py-2 font-semibold">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id} className="border-b border-border bg-panel align-top">
              <td className="px-3 py-3 font-medium">{lead.name || "Unknown"}</td>
              <td className="px-3 py-3">{lead.role}</td>
              <td className="px-3 py-3">{lead.company}</td>
              <td className="px-3 py-3">
                {lead.website ? (
                  <a className="text-primary underline-offset-2 hover:underline" href={lead.website} target="_blank" rel="noreferrer">
                    Domain
                  </a>
                ) : (
                  ""
                )}
              </td>
              <td className="px-3 py-3">{lead.email}</td>
              <td className="px-3 py-3 capitalize">{lead.platform.replaceAll("_", " ")}</td>
              <td className="px-3 py-3">
                <span className={`inline-flex min-w-12 justify-center rounded px-2 py-1 text-xs font-semibold ${scoreClass(lead.lead_score)}`}>
                  {lead.lead_score}
                </span>
              </td>
              <td className="px-3 py-3">{lead.post_date ? new Date(lead.post_date).toLocaleDateString() : ""}</td>
              <td className="px-3 py-2">
                {lead.post_url && (
                  <IconButton title="View details" onClick={() => chrome.tabs.create({ url: lead.post_url })}>
                    <ExternalLink className="size-4" />
                  </IconButton>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {leads.length === 0 && <div className="px-4 py-10 text-center text-sm text-muted">No leads yet.</div>}
    </div>
  );
}
