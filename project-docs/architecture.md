# Folder Structure

```
README.md               Human entry point
AGENTS.md               Cross-tool agent notes (Codex, other coding assistants)
.claude/
  CLAUDE.md             Operating instructions for Claude Code
  rules/guardrails.md   Technical rules, UA classification patterns, flag thresholds, saving estimates
  skills/                Analytics skills (preflight, run, quickcheck, compare, report-edit, clear-analytics-data) + URL/domain/IP tools (url-check, ik-debug, transform-test, ip-lookup, origin-vendor, imagekit-cname-check, custom-domain-request)
agent/
  prompt.md             Main analysis prompt — Claude reads this when running an analysis
  extract.py            Pre-processor — compresses raw JSON into a compact summary
  docs/                 Reference docs the prompt itself points to (tracked)
data/                   Runtime data — gitignored, except folder structure + input/README.md
  input/                Drop customer JSONs here
  extracted/            Generated compact summaries (produced by extract.py)
  output/               Analysis outputs — [account]/ holds the current review; older ones move to [account]/archive/[period]/
  reference-outputs/    Example analyses — Vax, Morphic, Popopo (older single-file format)
archive/                Old prompt versions, retired scripts — gitignored, except README.md
  test/                 Prompt-development test runs — customer-report-prompt-notes.md is active reference for prompt work, not disposable
setup/
  installation.md       One-time setup guide
project-docs/
  phases.md             Full phase-by-phase breakdown (0–7)
  architecture.md       This file
```

## What's gitignored

- `data/*` — all customer JSONs, extracted files, outputs, and reference-outputs. Only the folder structure itself and `data/input/README.md` are tracked, so a fresh clone gets a working skeleton with no customer data attached.
- `archive/*` — all drafts and old prompt/guardrails versions. Only `archive/README.md` is tracked.
- `status.md` — internal planning doc, not needed to run the agent.
