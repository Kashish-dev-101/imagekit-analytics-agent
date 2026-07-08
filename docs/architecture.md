# Folder Structure

```
README.md               Human entry point
AGENTS.md               Cross-tool agent notes (Codex, other coding assistants)
.claude/
  CLAUDE.md             Operating instructions for Claude Code
  rules/guardrails.md   Technical rules, UA classification patterns, flag thresholds, saving estimates
  skills/                Analytics skills (preflight, analytics-run, quickcheck, compare, report-edit)
agent/
  prompt.md             Main analysis prompt — Claude reads this when running an analysis
  extract.py            Pre-processor — compresses raw JSON into a compact summary
  docs/                 Reference docs the prompt itself points to (tracked)
data/                   Runtime data — gitignored, except folder structure + input/README.md
  input/                Drop customer JSONs here
  extracted/            Generated compact summaries (produced by extract.py)
  output/               Working output location during runs
reference-outputs/      Example analyses — gitignored, local only — Vax, Morphic, Popopo (older single-file format)
archive/                Old prompt versions, retired scripts — gitignored, except README.md
  test/                 Prompt-development test runs
setup/
  installation.md       One-time setup guide
docs/
  phases.md             Full phase-by-phase breakdown (0–8)
  architecture.md        This file
  examples.md           Reference example analyses
```

## What's gitignored

- `data/*` — all customer JSONs, extracted files, and outputs. Only the folder structure itself and `data/input/README.md` are tracked, so a fresh clone gets a working skeleton with no customer data attached.
- `archive/*` — all drafts and old prompt/guardrails versions. Only `archive/README.md` is tracked.
- `reference-outputs/` — real customer example analyses, local only.
- `status.md`, `restructure-log.md` — internal planning docs, not needed to run the agent.
