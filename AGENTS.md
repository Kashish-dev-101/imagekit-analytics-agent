# AGENTS.md — ImageKit Analytics Agent

Instructions for Codex and other coding assistants working in this repository.
Designed to coexist with `CLAUDE.md` — both files should remain aligned in intent.

---

## Operating Roles

Default to **CSM Mode**.

Only switch to **Prompt Maintainer Mode** when the user explicitly asks for prompt-development work or explicitly authorizes editing prompt-maintenance files such as `prompt.md`, `guardrails.md`, `AGENTS.md`, `CLAUDE.md`, or prompt-iteration files in `archive/test/`.

### CSM Mode

This is the default mode for normal customer work.

Allowed:
- Run analyses from `data/input/`
- Write new outputs to `data/output/`
- Edit an existing `[account]-customer-report.md` only

Not allowed unless the user explicitly switches to Prompt Maintainer Mode:
- Edit `prompt.md`
- Edit `guardrails.md`
- Edit `AGENTS.md`
- Edit `CLAUDE.md`
- Edit prompt-iteration notes or drafts in `archive/test/`
- Create new prompt-work files in `archive/test/`

### Prompt Maintainer Mode

Use this mode only for prompt-development and repo-maintenance work explicitly requested by the user.

Allowed:
- Edit `prompt.md`, `guardrails.md`, `AGENTS.md`, `CLAUDE.md`
- Update `test/customer-report-prompt-notes.md`
- Create or revise prompt-development drafts in `archive/test/`
- Update handoff context for the next agent/session

---

## Session Notes — Prompt Maintainer Workflow

When in Prompt Maintainer Mode, read `test/customer-report-prompt-notes.md` before starting work. The **Next Up** section at the top is the task list. Work through it in order.

After completing prompt-maintainer work:
- Tick off completed items in Next Up
- Update the decisions body if anything changed
- Preserve context for the next session
- Leave clear next steps if anything remains
- Do not create new notes files unless the user explicitly asks for a separate workstream

This file is the handoff doc between sessions and between agents for prompt iteration. It is different from the analysis trace files (which are per-run evidence and calculation logs for customer outputs).

---

## Project Purpose

This project analyses ImageKit analytics JSON exports and produces three output files per customer:

1. **Full technical analysis** — traffic, format delivery, UA breakdown, geography, top assets, transformations, cache, errors, optimisation opportunities
2. **Customer-facing report** — non-technical summary for account review calls
3. **Internal trace** — evidence and calculation log showing what was read, calculated, and which rules support each finding

Core project files:
- `prompt.md` — main analysis prompt, defines all phases
- `guardrails.md` — technical rules, UA classification patterns, flag thresholds, saving estimates

---

## Folder Structure

```
agent/
  prompt.md             Main analysis prompt — Claude reads this when running an analysis
  extract.py            Pre-processor — compresses raw JSON into a compact summary
  docs/                 Reference docs for customer-facing recommendations (tracked)
.claude/
  rules/guardrails.md   Technical rules, UA classification patterns, thresholds, saving estimates
  skills/               Analytics skills (preflight, run, quickcheck, compare, report-edit)
data/                   Runtime data (gitignored — customer data stays local)
  input/                Customer JSON exports
  extracted/            Generated compact summaries (produced by extract.py)
  output/               Working output location during runs
archive/                Old prompt versions, retired scripts
  test/                 Prompt-development test runs (gitignored)
```

---

## How to Handle a Run Request

When the user asks to run an analysis:

1. **Check for an existing extracted file** — look for `data/extracted/[account]-extracted.txt`. If it exists, use it. If not, run the extractor first:
   ```bash
   python3 agent/extract.py data/input/[filename].json > data/extracted/[account]-extracted.txt
   ```
2. **Read `guardrails.md`** — follow all rules throughout the entire run.
3. **Read `prompt.md`** — follow it exactly, phase by phase.
4. **Incorporate any account context** the user provided in their message — weave it into the analysis and customer report where relevant.
5. **Save all three output files to `data/output/`**.

Only save to `archive/test/` when the user has explicitly switched to Prompt Maintainer Mode and asked for a prompt test run.

---

## Output Naming Convention

`[account]-[period]-[type].md`

| Type | Example |
|------|---------|
| Full analysis | `acme-march-2026-analysis.md` |
| Trace | `acme-march-2026-trace.md` |
| Customer report | `acme-march-2026-customer-report.md` |

All outputs go to `data/output/`.
Only use `archive/test/` for explicit Prompt Maintainer Mode test runs.

---

## File Protection Rules

These apply at all times, regardless of what the user asks.

- **`[account]-trace.md` and `[account]-analysis.md` are read-only after initial generation.** Never modify them — not for edits, context updates, or corrections — unless the user explicitly asks to run a new analysis with new JSON data.
- **The only file to modify after generation is `[account]-customer-report.md`.** All post-analysis requests (edits, tone changes, reprioritisation) go there only.
- **When editing the customer report**, pull data from the analysis and trace files only. Do not re-read the JSON or re-run any phase.
- **If a request is ambiguous** — e.g. "update the analysis", "revise the report" — do not touch any file. Ask: *"Do you want to re-run the full analysis with new data, or make changes to the customer report only?"* Wait for the answer.
- **A new analysis is only triggered when** the user provides a new JSON file and explicitly asks to run the analysis.

---

## Key Technical Rules

Full detail in `guardrails.md`. Critical rules to apply from the start:

- **Check truncation first** — verify that dimensional breakdowns (formatWise, deviceDistribution, country) sum close to `request.total` before drawing conclusions. If they cap at 10–15% of total, the data is truncated — flag it prominently.
- **WebP ≠ AVIF** — WebP is automatic. AVIF must be explicitly enabled in account settings. Never treat them as the same.
- **`tr=orig` is video-only** — intermediate first-request response for uncached video transformations. Not an error.
- **`f-auto` + native apps** — doesn't work for OkHttp/URLSession/Dart clients. Explicit `f-webp` needed in image URLs.
- **VPU is video-only** — never reference VPU in image findings.

---

## Data and Safety Rules

- Treat customer analytics exports as sensitive — never log, expose, or commit them.
- Customer JSONs and extracted files belong in `data/input/` (gitignored).
- Completed analyses belong in `data/output/` (gitignored).
- `archive/test/` is for prompt-development and agent-maintenance work only, not normal CSM/customer operations.

---

## Non-Destructive Rule

- Do not rewrite or auto-refactor `prompt.md`, `guardrails.md`, `AGENTS.md`, or `CLAUDE.md` unless explicitly requested.
- By default, only edit files the user has asked about.
- If unsure, create new output files rather than altering existing baseline docs.
- Never delete analysis artifacts unless explicitly asked.

## Gists

Always create gists as **secret**. Never use `--public`. Default (`gh gist create` with no flag) = secret. Only use `--public` if the user explicitly asks.
