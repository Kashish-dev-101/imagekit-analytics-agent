# Phase-by-Phase Breakdown

The agent runs a structured 9-phase analysis process (0–8), all defined in `agent/prompt.md`.

| Phase | What it does |
|-------|-------------|
| 0 — Data Integrity | Checks whether dimensional breakdowns are complete or truncated (known platform bug) |
| 1 — Traffic Summary | Requests, bandwidth, daily trend, URL patterns, top countries, top referrers |
| 2 — Format Delivery | What formats ImageKit served — WebP, AVIF, JPEG, WebM, MP4 — and what's missing |
| 3 — Traffic Sources | Classifies all traffic: web browser, native app, bot, in-app browser, server-side |
| 4 — Resize Coverage | How widely transforms are used, which high-traffic assets have no resize applied |
| 5 — Top Assets | Deep dive on highest-bandwidth images and videos — per-view size, format, transform |
| 6 — Transform Analysis | Transform sprawl, near-duplicate widths, malformed strings, cache hit rate |
| 7 — Top IPs | Who is making the most requests — app servers, bots, scrapers, CDN nodes |
| 8 — VPU Consumption | Video processing unit usage, thumbnail costs, first-request processing spikes |

After every phase, findings are appended to the analysis file and a structured trace entry (Data Read → Arithmetic → Decision) is appended to the trace file — never batched to the end.

Once all 9 phases are done, the two internal files (analysis + trace) are finalized and the customer-facing report is built from them.

This table is a summary. For the exact detection logic, thresholds, and rules behind each phase, see `agent/prompt.md` and `.claude/rules/guardrails.md` — those are the source of truth, not this file.
