# data/input/

Drop customer analytics JSON exports here before running an analysis.

Files here are local-only (gitignored) — safe for customer data. Only this README is tracked in git.

## What's in this folder

- `[account].json` — raw analytics export from the ImageKit dashboard (local only)

## Usage

1. Drop the customer's JSON export here, e.g. `data/input/girnar.json`
2. In Claude Code, say: "Run the analysis for [account] — JSON is `data/input/[filename].json`, period is [month year]"
3. Optionally add any account context in your message (call purpose, known concerns, etc.)
4. Claude resolves the file via the `analytics-preflight` skill, runs `agent/extract.py` to produce a compact summary in `data/extracted/`, then proceeds with the full analysis

Outputs are saved to `data/output/[account]/`.
