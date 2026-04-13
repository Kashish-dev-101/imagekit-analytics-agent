# input/

Drop customer analytics JSON exports here before running an analysis.

Files here are local-only (gitignored) — safe for customer data.

## What's in this folder

- `extract.py` / `extract.js` — extractor scripts that compress the raw JSON into a compact summary
- `[account].json` — raw analytics export from ImageKit dashboard (local only)
- `[account]-extracted.txt` — pre-processed summary produced by the extractor (generated automatically, local only)

## Usage

1. Drop the customer's JSON export here
2. In Claude Code, say: "Run the analysis for [account] — JSON is `input/[filename].json`, period is [month year]"
3. Optionally add any account context in your message (call purpose, known concerns, etc.)
4. Claude will run the extractor, then proceed with the full analysis

Outputs are saved to `outputs/`.
