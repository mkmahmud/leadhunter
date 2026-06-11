import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(214 18% 86%)",
        background: "hsl(210 20% 98%)",
        foreground: "hsl(220 24% 12%)",
        muted: "hsl(215 16% 47%)",
        panel: "hsl(0 0% 100%)",
        primary: "hsl(173 78% 28%)",
        accent: "hsl(28 86% 54%)"
      }
    }
  },
  plugins: []
} satisfies Config;
