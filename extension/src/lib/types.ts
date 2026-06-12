export const platforms = [
  "reddit",
  "linkedin",
  "twitter",
  "indiehackers",
  "producthunt",
  "medium",
  "github",
  "stackoverflow",
  "youtube",
  "facebook",
  "startup_communities",
  "hackernews",
  "public_blogs",
  "company_blogs"
] as const;

export type Platform = (typeof platforms)[number];

export type Lead = {
  id: string;
  name: string;
  role: string;
  company: string;
  website: string;
  linkedin: string;
  email: string;
  phone: string;
  industry: string;
  location: string;
  platform: string;
  post_url: string;
  post_content: string;
  post_date: string | null;
  intent_summary: string;
  lead_score: number;
  category: "Hot" | "Warm" | "Cold";
  created_at: string;
};

export type CapturedLead = {
  name?: string;
  role?: string;
  company?: string;
  website?: string;
  linkedin?: string;
  email?: string;
  phone?: string;
  location?: string;
  industry?: string;
  platform: string;
  post_url?: string;
  post_content: string;
  post_date?: string | null;
};

export type SearchPayload = {
  platforms: Platform[];
  date_range: {
    preset: "today" | "last_24_hours" | "last_3_days" | "last_7_days" | "last_30_days" | "custom";
    start_date?: string;
    end_date?: string;
  };
  keywords: string[];
  intent_categories: string[];
  filters: {
    only_founders: boolean;
    only_ceos: boolean;
    only_ctos: boolean;
    only_decision_makers: boolean;
    must_have_company_domain: boolean;
    must_have_email: boolean;
    minimum_lead_score: number;
    country?: string;
    industry?: string;
    company_size?: string;
  };
};
