# Phase-by-Phase Breakdown

The agent runs a structured 8-phase analysis process (0–7), all defined in `agent/prompt.md`.

| Phase | What it does |
|-------|-------------|
| 0 — Data Integrity | Checks whether dimensional breakdowns are complete or truncated (known platform bug) |
| 1 — Traffic Summary | Requests, bandwidth, daily trend, URL patterns, top countries, top referrers |
| 2 — Format Delivery | What formats ImageKit served — WebP, AVIF, JPEG, WebM, MP4 — and what's missing |
| 3 — Traffic Sources | Classifies all traffic: web browser, native app, bot, in-app browser, server-side |
| 4 — Resize, Transform Coverage & Top Assets | Transform adoption rate, top image/video asset audit (per-view size, resize params, format params, dimension fetch), top others |
| 5 — Transformation Analysis | Transform sprawl, near-duplicate widths, ABS detection, signed URL cache fragmentation, cache hit rate |
| 6 — Top IPs | Flags IPs above concentration thresholds — request %, bandwidth %, avg asset size. Lookup + classification (CDN, cloud provider, residential, unknown) |
| 7 — VPU Consumption | Video processing unit usage, resolution tier breakdown, AV1 flag, thumbnail cost |

After every phase, findings are appended to the analysis file and a structured trace entry (Data Read → Arithmetic → Decision) is appended to the trace file — never batched to the end.

Once all 8 phases are done, the two internal files (analysis + trace) are finalized and the customer-facing report is built from them.

This table is a summary. For the exact detection logic, thresholds, and rules behind each phase, see `agent/prompt.md` and `.claude/rules/guardrails.md` — those are the source of truth, not this file.
