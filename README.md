# ImageKit Analytics Agent

A Claude Code agent for analysing ImageKit monthly analytics JSON exports. Drop in a customer's data, ask Claude to run the analysis, and get a full technical analysis plus a customer-facing report ready for the account review call.

---

## What It Produces

For each customer, the agent creates three files:

| File | Audience | Purpose |
|------|----------|---------|
| `[account]-[period]-analysis.md` | Internal | Full technical findings — every phase, every flag, all numbers |
| `[account]-[period]-trace.md` | Internal | Reasoning log — what was read, how calculations were done, why things were flagged |
| `[account]-[period]-customer-report.md` | Customer-facing | Non-technical summary for the account review call — what's working, what to fix, questions for the call |

---

## Operating Modes

Default to **CSM Mode** for normal customer work.

- In `CSM Mode`, use `data/input/` and `data/output/` only. Run analyses, generate outputs, and edit existing customer report files when needed.
- `archive/test/` is for prompt-development and agent-maintenance work only.
- Only switch to **Prompt Maintainer Mode** when prompt-development work is explicitly requested and editing `prompt.md`, `guardrails.md`, repo instruction files, or prompt-iteration files in `archive/test/` is intentionally authorized.

See `AGENTS.md` for the full role and file-editing policy.

---

## Getting Started

First time? Follow **[setup/installation.md](./setup/installation.md)** to install Node.js, VS Code, Claude Code, and Python. Takes about 10 minutes and only needs to be done once.

---

## How to Use

### 1. Add the customer's JSON

Drop the analytics JSON export from the ImageKit dashboard into the `data/input/` folder.

```
data/input/girnar.json
```

### 2. Open Claude Code in this project folder

```bash
cd "ImageKit Analytics Agent"
claude
```

### 3. Tell Claude to run the analysis

In the chat, say something like:

> "Run the analysis for Girnar — the JSON is `data/input/girnar.json`, period is March 2026."

You can also add account context in the same message — anything that should shape the findings or report tone:

> "Run the analysis for Girnar — JSON is `data/input/girnar.json`, March 2026. This is a renewal call and they've been asking about bandwidth costs."

Claude handles everything from there: running the extractor, reading the prompt, working through all analysis phases, and saving the three output files to `data/output/`.

### 4. Review the outputs

All three files land in `data/output/`:

```
data/output/girnar-march-2026-analysis.md
data/output/girnar-march-2026-trace.md
data/output/girnar-march-2026-customer-report.md
```

The **customer report** is what you bring to the call. The **analysis** and **trace** are reference — use them if you need to go deeper on a finding or verify a number.

### For prompt-development test runs

If you're explicitly doing prompt-development work, tell Claude to save to `archive/test/` instead:

> "Run the analysis for Girnar — JSON is `data/input/girnar.json`, March 2026. Save to `archive/test/` — this is a test run."

---

## Folder Structure

```
README.md               This file
AGENTS.md               Cross-tool agent notes (Codex, other coding assistants)
.claude/
  CLAUDE.md             Operating instructions for Claude Code
  rules/guardrails.md   Technical rules, UA classification patterns, flag thresholds, saving estimates
  skills/               Analytics skills (preflight, analytics-run, quickcheck, compare, report-edit)
agent/
  prompt.md             Main analysis prompt — Claude reads this when running an analysis
  extract.py            Pre-processor — compresses raw JSON into a compact summary
  docs/                 Reference docs for customer-facing recommendations (tracked)
data/                   Runtime data — gitignored (customer data stays local)
  input/                Drop customer JSONs here
  extracted/            Generated compact summaries (produced by extract.py)
  output/               Working output location during runs
reference-outputs/      Example analyses — gitignored, local only — Vax, Morphic, Popopo (older single-file format)
archive/                Old prompt versions, retired scripts
  test/                 Prompt-development test runs (gitignored)
setup/
  installation.md       One-time setup guide
```

**What's gitignored:**
- `data/` — all customer JSONs, extracted files, and outputs
- `archive/test/` — all test drafts (README tracked)

---

## How the Agent Works

The agent follows a structured 8-phase analysis process, all defined in `prompt.md`:

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

After all phases, Claude writes the two internal files and then the customer-facing report.

---

## Key Rules (summary — see `guardrails.md` for full detail)

- **Truncation check first** — high-traffic accounts often have dimensional data capping at 10–15% of total. Always verify before drawing format or device conclusions.
- **WebP ≠ AVIF** — WebP is automatic. AVIF must be enabled by ImageKit on the account. Never treat them as the same.
- **Native apps don't get format optimisation automatically** — Dart/Flutter and iOS apps don't send `Accept` headers. They need explicit `f-webp` in image URLs.
- **`tr=orig` is not an error** — it's an intermediate response for first-time uncached video transformations.
- **VPU is video-only** — never reference VPU in image findings.

---

## Reference Examples

Older single-file analyses in `reference-outputs/` — produced before the 3-file structure, still useful as content references:

| Account | Period | Notes |
|---------|--------|-------|
| Vax | March 2026 | High-traffic e-commerce, Cloudinary URL rewriter, strong WebP, UGC video gaps |
| Morphic | March 2026 | AI-generated content platform, Claude-User in top traffic sources, PNG optimisation gap |
| Popopo | March 2026 | `reference-outputs/popopo-march-2026.md` |
