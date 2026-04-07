# CLAUDE.md — ImageKit Analytics Agent

This project is an AI agent prompt for analysing ImageKit monthly analytics JSON exports. It takes raw account data and produces a full technical analysis + customer-facing talking points.

---

## What This Project Does

Given a customer's ImageKit analytics JSON export, the agent produces two outputs:

1. **Full technical analysis** — traffic overview, format delivery, UA breakdown, geography, top assets, transformation analysis, cache & errors, optimization opportunities
2. **Customer talking points** — non-technical summary for use in calls and account reviews

---

## Current State

- `prompt.md` — Main analysis prompt. **Work in progress** — being rebuilt with a more detailed technical process
- `guardrails.md` — Technical rules (format delivery, VPU, truncation bug, inference flags). Ready.
- `schema.md` — JSON field guide — what each key reveals. Ready.
- `outputs/` — Example outputs from real account analyses (Vax, Morphic, Popopo)

---

## How to Use

1. Drop the customer's analytics JSON into the `test/` folder (gitignored — safe for customer data)
2. Open Claude Code in the root of this project
3. Paste the prompt from `prompt.md` into the chat, filling in customer name, date range, and JSON filename
4. Claude will produce two files in `outputs/`

---

## Folder Structure

```
prompt.md           Main analysis prompt — paste into Claude Code
guardrails.md       Technical rules Claude must follow during analysis
schema.md           JSON field guide — what each analytics key reveals
outputs/            Completed analyses (gitignored — customer data)
test/               Working space for test runs (gitignored — local only)
version-control/    Archived prompt versions (gitignored — local only)
```

**Gitignored (local only — may or may not exist on this machine):**
- `outputs/` — all customer account analyses
- `test/` — JSON files and draft outputs during testing
- `version-control/` — older prompt versions

---

## Output Naming Convention

`[account]-[period]-[type].md`

| Type | Example |
|------|---------|
| Full analysis | `vax-march-2026-analysis.md` |
| Talking points | `vax-march-2026-talking-points.md` |

Save all outputs to `outputs/`.

---

## Key Technical Rules (Read guardrails.md for full detail)

- **Check truncation first** — before drawing any conclusions from dimensional breakdowns (formatWise, deviceTypeDistribution, country), verify they sum close to `request.total`. If they cap at 10–15% of total, the data is truncated — this is a known platform bug. Flag it prominently.
- **WebP vs AVIF** — WebP is automatic (no config needed). AVIF must be explicitly enabled in account settings. Never treat them as the same setting.
- **`tr=orig` is video-only** — intermediate first-request response for uncached video transformations. Not an error.
- **`f-auto` + native apps** — doesn't work for OkHttp/URLSession clients. Explicit `f-webp` needed.
- **VPU** — consumed once per unique transformation on first request. 30 VPU per thumbnail.

---

## Reference Outputs

| Account | Period | Notes |
|---------|--------|-------|
| Vax | March 2026 | High-traffic e-commerce, Cloudinary URL rewriter, strong WebP, UGC video gaps |
| Morphic | March 2026 | AI-generated content platform, Claude-User in top traffic sources, PNG optimization gap |
| Popopo | March 2026 | See `outputs/popopo-march-2026.md` |
