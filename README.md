# ImageKit Analytics Agent

A reusable Claude Code agent for analysing ImageKit monthly analytics JSON exports. Takes raw account data and produces a full technical analysis + customer-facing talking points.

---

## What It Does

Given a customer's ImageKit analytics JSON, the agent produces:

1. **Quick account summary** — who the customer is, traffic volume, bandwidth, daily trends
2. **Format delivery analysis** — WebP/AVIF coverage, video WebM, optimization gaps
3. **UA & device breakdown** — browser mix, mobile %, native app clients, bots, AI agents
4. **Geography** — top countries by requests and bandwidth, anomalies
5. **Top assets** — highest bandwidth and highest frequency images and videos
6. **Optimization opportunities** — data-backed, referenced against ImageKit docs
7. **Customer talking points** — non-technical summary for calls and account reviews

---

## How to Use

1. Drop the customer's analytics JSON into a working folder
2. Open Claude Code in that folder
3. Paste the prompt from `prompt.md` into the chat
4. Attach or reference the JSON file
5. Claude will produce a full analysis + talking points

---

## Files

| File | Purpose |
|------|---------|
| `prompt.md` | Main analysis prompt — paste this into Claude |
| `guardrails.md` | Technical rules Claude must follow when analysing ImageKit data |
| `schema.md` | JSON field guide — what each key reveals and what to look for |
| `outputs/` | Example outputs from real account analyses |

---

## Example Outputs

| Account | Period | Files |
|---------|--------|-------|
| Vax | March 2026 | `outputs/vax-march-2026.md` |
| Morphic | March 2026 | `outputs/morphic-march-2026.md` |
| Popopo | March 2026 | `outputs/popopo-march-2026.md` |
