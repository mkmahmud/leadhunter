import { zodResolver } from "@hookform/resolvers/zod";
import { CalendarDays, Play, RotateCcw } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { startSearch } from "../lib/api";
import { platforms, type SearchPayload } from "../lib/types";
import { useSearchStore } from "../store/searchStore";
import { Button, Checkbox, Input, Section } from "./primitives";

const intentCategories = [
  "Website Design",
  "Web Development",
  "SaaS",
  "MVP",
  "AI Development",
  "Automation",
  "Technical Co-Founder",
  "API Integration"
];

const schema = z.object({
  platforms: z.array(z.enum(platforms)).min(1),
  preset: z.enum(["today", "last_24_hours", "last_3_days", "last_7_days", "last_30_days", "custom"]),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
  keywords: z.string().min(2),
  intent_categories: z.array(z.string()),
  only_founders: z.boolean(),
  only_ceos: z.boolean(),
  only_ctos: z.boolean(),
  only_decision_makers: z.boolean(),
  must_have_company_domain: z.boolean(),
  must_have_email: z.boolean(),
  minimum_lead_score: z.coerce.number().min(0).max(100),
  country: z.string().optional(),
  industry: z.string().optional(),
  company_size: z.string().optional()
});

type FormValues = z.infer<typeof schema>;

const defaultKeywords = [
  "need website developer",
  "looking for web developer",
  "need SaaS developer",
  "need website redesign",
  "looking for technical help",
  "need MVP developer",
  "need AI integration"
].join("\n");

export function SearchForm() {
  const setJob = useSearchStore((state) => state.setJob);
  const setStatus = useSearchStore((state) => state.setStatus);
  const { register, handleSubmit, watch, reset, formState } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      platforms: ["reddit", "github", "hackernews", "indiehackers"],
      preset: "last_7_days",
      keywords: defaultKeywords,
      intent_categories: ["Web Development", "SaaS", "MVP", "AI Development"],
      only_founders: false,
      only_ceos: false,
      only_ctos: false,
      only_decision_makers: true,
      must_have_company_domain: false,
      must_have_email: false,
      minimum_lead_score: 50
    }
  });
  const preset = watch("preset");

  async function submit(values: FormValues) {
    setStatus("queued");
    const payload: SearchPayload = {
      platforms: values.platforms,
      date_range: { preset: values.preset, start_date: values.start_date, end_date: values.end_date },
      keywords: values.keywords
        .split(/\n|,/)
        .map((item) => item.trim())
        .filter(Boolean),
      intent_categories: values.intent_categories,
      filters: {
        only_founders: values.only_founders,
        only_ceos: values.only_ceos,
        only_ctos: values.only_ctos,
        only_decision_makers: values.only_decision_makers,
        must_have_company_domain: values.must_have_company_domain,
        must_have_email: values.must_have_email,
        minimum_lead_score: values.minimum_lead_score,
        country: values.country,
        industry: values.industry,
        company_size: values.company_size
      }
    };
    const job = await startSearch(payload);
    setJob(job.job_id, "running");
  }

  return (
    <form onSubmit={handleSubmit(submit)} className="bg-panel">
      <Section title="Platforms">
        <div className="grid grid-cols-2 gap-x-3">
          {platforms.map((platform) => (
            <Checkbox key={platform} label={platform.replaceAll("_", " ")} value={platform} {...register("platforms")} />
          ))}
        </div>
      </Section>

      <Section title="Date Range">
        <div className="flex items-center gap-2">
          <CalendarDays className="size-4 text-muted" />
          <select className="focus-ring h-9 flex-1 rounded-md border border-border bg-white px-2 text-sm" {...register("preset")}>
            <option value="today">Today</option>
            <option value="last_24_hours">Last 24 Hours</option>
            <option value="last_3_days">Last 3 Days</option>
            <option value="last_7_days">Last 7 Days</option>
            <option value="last_30_days">Last 30 Days</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
        {preset === "custom" && (
          <div className="mt-3 grid grid-cols-2 gap-2">
            <Input type="date" {...register("start_date")} />
            <Input type="date" {...register("end_date")} />
          </div>
        )}
      </Section>

      <Section title="Keywords">
        <textarea className="focus-ring min-h-28 w-full rounded-md border border-border bg-white p-3 text-sm" {...register("keywords")} />
      </Section>

      <Section title="Intent Categories">
        <div className="grid grid-cols-2 gap-x-3">
          {intentCategories.map((category) => (
            <Checkbox key={category} label={category} value={category} {...register("intent_categories")} />
          ))}
        </div>
      </Section>

      <Section title="Lead Filters">
        <div className="grid gap-1">
          <Checkbox label="Only Founders" {...register("only_founders")} />
          <Checkbox label="Only CEOs" {...register("only_ceos")} />
          <Checkbox label="Only CTOs" {...register("only_ctos")} />
          <Checkbox label="Only Decision Makers" {...register("only_decision_makers")} />
          <Checkbox label="Must Have Company Domain" {...register("must_have_company_domain")} />
          <Checkbox label="Must Have Email" {...register("must_have_email")} />
        </div>
        <div className="mt-3 grid gap-2">
          <label className="text-xs font-medium text-muted">Minimum Lead Score</label>
          <Input type="number" min={0} max={100} {...register("minimum_lead_score")} />
          <Input placeholder="Country Filter" {...register("country")} />
          <Input placeholder="Industry Filter" {...register("industry")} />
          <Input placeholder="Company Size Filter" {...register("company_size")} />
        </div>
      </Section>

      <div className="sticky bottom-0 flex gap-2 border-t border-border bg-panel p-4">
        <Button className="flex-1" disabled={formState.isSubmitting}>
          <Play className="size-4" />
          Search
        </Button>
        <Button type="button" className="bg-accent px-3" onClick={() => reset()}>
          <RotateCcw className="size-4" />
        </Button>
      </div>
    </form>
  );
}
