import type { CapturedLead } from "./lib/types";

const INTENT_RE =
  /\b(need|looking for|hire|hiring|seeking|recommend|help building|build|redesign|developer|technical co-founder|mvp|saas|api integration|ai integration|automation|website)\b/i;

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "SCRAPE_VISIBLE_LEADS") return false;
  sendResponse({ items: scrapeVisibleLeads() });
  return false;
});

function scrapeVisibleLeads(): CapturedLead[] {
  const candidates = collectCandidateElements();
  const seen = new Set<string>();
  const leads: CapturedLead[] = [];
  for (const element of candidates) {
    if (!isVisible(element)) continue;
    const text = normalizeText(element.textContent ?? "");
    if (text.length < 60 || !INTENT_RE.test(text)) continue;
    const key = text.slice(0, 220);
    if (seen.has(key)) continue;
    seen.add(key);
    leads.push(toCapturedLead(element, text));
    if (leads.length >= 100) break;
  }
  return leads;
}

function collectCandidateElements(): Element[] {
  const selectors = [
    "article",
    "[role='article']",
    "[data-testid='tweet']",
    "[data-testid='post-container']",
    "shreddit-post",
    ".thing",
    ".athing",
    ".comment",
    ".js-comment",
    ".Box-row",
    ".feed-shared-update-v2",
    ".update-components-text",
    ".post",
    ".discussion-timeline-actions",
    "li"
  ];
  const elements = selectors.flatMap((selector) => [...document.querySelectorAll(selector)]);
  return elements.length ? elements : [...document.querySelectorAll("main div, body div")].slice(0, 500);
}

function toCapturedLead(element: Element, text: string): CapturedLead {
  const url = findBestUrl(element);
  return {
    name: findAuthor(element),
    company: hostLabel(location.hostname),
    website: location.origin,
    platform: detectPlatform(location.hostname),
    post_url: url,
    post_content: text,
    post_date: findDate(element)
  };
}

function findBestUrl(element: Element): string {
  const anchor = element.querySelector<HTMLAnchorElement>("a[href*='/comments/'], a[href*='/status/'], a[href*='/posts/'], a[href*='/issues/'], a[href*='item?id='], a[href]");
  if (!anchor?.href) return location.href;
  try {
    return new URL(anchor.href, location.href).href;
  } catch {
    return location.href;
  }
}

function findAuthor(element: Element): string {
  const selectors = [
    "[data-testid='User-Name']",
    "a[href*='/user/']",
    "a[href*='reddit.com/user/']",
    "a[href*='github.com/']",
    ".author",
    ".hnuser",
    ".usertext",
    ".feed-shared-actor__name"
  ];
  for (const selector of selectors) {
    const text = normalizeText(element.querySelector(selector)?.textContent ?? "");
    if (text && text.length <= 80) return text;
  }
  return "";
}

function findDate(element: Element): string | null {
  const time = element.querySelector<HTMLTimeElement>("time[datetime]");
  if (time?.dateTime) return new Date(time.dateTime).toISOString();
  return null;
}

function detectPlatform(hostname: string): string {
  const host = hostname.toLowerCase();
  if (host.includes("reddit")) return "reddit";
  if (host.includes("linkedin")) return "linkedin";
  if (host.includes("twitter") || host.includes("x.com")) return "twitter";
  if (host.includes("github")) return "github";
  if (host.includes("news.ycombinator")) return "hackernews";
  if (host.includes("youtube")) return "youtube";
  if (host.includes("facebook")) return "facebook";
  if (host.includes("stackoverflow")) return "stackoverflow";
  if (host.includes("medium")) return "medium";
  if (host.includes("producthunt")) return "producthunt";
  if (host.includes("indiehackers")) return "indiehackers";
  return "public_blogs";
}

function hostLabel(hostname: string): string {
  return hostname.replace(/^www\./, "");
}

function isVisible(element: Element): boolean {
  const rect = element.getBoundingClientRect();
  const style = window.getComputedStyle(element);
  return rect.width > 0 && rect.height > 0 && rect.bottom >= 0 && rect.top <= window.innerHeight && style.visibility !== "hidden" && style.display !== "none";
}

function normalizeText(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}
