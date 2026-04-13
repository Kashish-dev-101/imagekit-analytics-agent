# CLAUDE.md — ImageKit Analytics Agent

This project is an AI agent prompt for analysing ImageKit monthly analytics JSON exports. It takes raw account data and produces a full technical analysis + customer-facing talking points.

---

## What This Project Does

Given a customer's ImageKit analytics JSON export, the agent produces three outputs:

1. **Full technical analysis** — traffic overview, format delivery, UA breakdown, geography, top assets, transformation analysis, cache & errors, optimization opportunities
2. **Customer-facing report** — non-technical summary for account review calls
3. **Internal trace** — reasoning log showing what was read, calculated, and why things were flagged

---

## Operating Mode

Default to **CSM Mode**.

In CSM Mode:
- Do not edit `prompt.md`, `guardrails.md`, `AGENTS.md`, `CLAUDE.md`, or prompt-development files in `test/`
- Run analyses from `input/`
- Save outputs to `outputs/`
- Only edit existing `[account]-customer-report.md` files for post-analysis changes

Only switch to **Prompt Maintainer Mode** when the user explicitly asks for prompt-development work or explicitly authorizes editing prompt/rules/notes files.

In Prompt Maintainer Mode:
- Read `test/customer-report-prompt-notes.md` before starting prompt work
- Use the `Next Up` section as the task list
- Update that same notes file in place after work with completed items, changed decisions, preserved context, and remaining next steps

---

## How to Use

1. Drop the customer's analytics JSON into `input/` (gitignored — safe for customer data)
2. Open Claude Code in the root of this project
3. Tell Claude: *"Run the analysis for [account] — the JSON is `input/[filename].json`, period is [month year]"*
4. Optionally add any account context in your message (call purpose, known concerns, renewal vs expansion, etc.)
5. Claude handles everything from there — extractor, analysis phases, and saving all three output files to `outputs/`

Use `test/` only for explicit prompt-maintainer test runs.

---

## How Claude Should Handle a Run Request

When the user asks to run an analysis:

1. **Check for an existing extracted file** — look for `input/[account]-extracted.txt`. If it exists, use it. If not, run the extractor first:
   ```bash
   python3 input/extract.py input/[filename].json > input/[account]-extracted.txt
   ```
2. **Read `prompt.md`** — this is the full analysis prompt. Follow it exactly, phase by phase.
3. **Read `guardrails.md`** — as instructed at the top of `prompt.md`.
4. **Incorporate any account context** the user provided in their message — weave it into the analysis and customer report where relevant.
5. **Save all three output files to `outputs/`**.

Only save to `test/` for explicit prompt-maintainer test work.

---

## Folder Structure

```
prompt.md           Main analysis prompt
guardrails.md       Technical rules Claude must follow during analysis
docs/               Reference docs for customer-facing recommendations — platform compatibility, best practices
input/              Customer JSON exports and extracted files (gitignored — local only)
outputs/            Completed analyses (gitignored — customer data)
outputs/examples/   Reference outputs — older single-file format
test/               For testing the agent itself (gitignored — local only)
version-control/    Archived prompt versions (gitignored — local only)
```

**Gitignored (local only — may or may not exist on this machine):**
- `input/` — customer JSONs and extracted files (except README)
- `outputs/` — all customer account analyses (outputs/examples/ is tracked)
- `test/` — agent test drafts (except README)
- `version-control/` — older prompt versions (except README)

---

## Output Naming Convention

`[account]-[period]-[type].md`

| Type | Example |
|------|---------|
| Full analysis | `girnar-march-2026-analysis.md` |
| Customer report | `girnar-march-2026-customer-report.md` |
| Trace | `girnar-march-2026-trace.md` |

Save all outputs to `outputs/`.

---

## File Protection Rules

These rules apply at all times, regardless of what the user asks.

- **`[account]-trace.md` and `[account]-analysis.md` are read-only after initial generation.** Never modify them for any reason — not for edits, not for context updates, not for corrections — unless the user explicitly says they want to run a brand new analysis with new JSON data.
- **The only file that should be modified after initial generation is `[account]-customer-report.md`.** All post-analysis requests (edits, context additions, reprioritisation, tone changes) go there only.
- **When adding or changing anything in the customer report**, pull data from `[account]-analysis.md` and `[account]-trace.md` only. Do not re-read the JSON, do not re-run any analysis phase. The analysis and trace files contain everything needed.
- **If a request is ambiguous** — e.g. "update the analysis", "can you change the findings", "revise the report" — do not touch any file. Ask first: *"Do you want to re-run the full analysis with new data, or make changes to the customer report only?"* Wait for the answer before doing anything.
- **A new analysis is only triggered when** the user provides a new JSON file and explicitly asks to run the analysis. Editing the customer report, adding account context, or refining recommendations does not count.

---

## Key Technical Rules (Read guardrails.md for full detail)

- **Check truncation first** — before drawing any conclusions from dimensional breakdowns (formatWise, deviceTypeDistribution, country), verify they sum close to `request.total`. If they cap at 10–15% of total, the data is truncated — this is a known platform bug. Flag it prominently.
- **WebP vs AVIF** — WebP is automatic (no config needed). AVIF must be explicitly enabled in account settings. Never treat them as the same setting.
- **`tr=orig` is video-only** — intermediate first-request response for uncached video transformations. Not an error.
- **`f-auto` + native apps** — doesn't work for OkHttp/URLSession clients. Explicit `f-webp` needed.
- **VPU** — consumed once per unique transformation on first request. 30 VPU per thumbnail.

---

## Reference Outputs

Stored in `outputs/examples/` — older single-file format (produced before the 3-file structure). Still useful as content references.

| Account | Period | Notes |
|---------|--------|-------|
| Vax | March 2026 | High-traffic e-commerce, Cloudinary URL rewriter, strong WebP, UGC video gaps |
| Morphic | March 2026 | AI-generated content platform, Claude-User in top traffic sources, PNG optimization gap |
| Popopo | March 2026 | See `outputs/examples/popopo-march-2026.md` |
