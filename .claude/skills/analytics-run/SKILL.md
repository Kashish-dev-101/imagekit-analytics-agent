---
name: analytics-run
description: Full ImageKit analytics analysis — all 8 phases, produces three files: internal technical analysis, evidence and calculation trace, and customer-facing report. Use for monthly account reviews or when you need the complete picture with recommendations.
when_to_use: Monthly analytics reviews, account review call prep, or when a quickcheck has flagged issues that need investigating. Produces 3 output files.
---

# /analytics-run — Full analysis (3 files)

## What this skill does

Runs the complete 8-phase analysis as defined in `agent/prompt.md` and produces three output files:
1. **Technical analysis** — full findings, every phase, all numbers, internal
2. **Trace** — evidence and calculation log showing what was read, reproducible calculations, and which rules support each finding, internal
3. **Customer report** — non-technical summary for the account review call, customer-facing

---

## 1. Resolve the input
Resolve which file to use per `.claude/skills/analytics-preflight/SKILL.md` (auto-pick when clear, ask when ambiguous; read and state the period from the data). Skip if preflight already resolved it.

## 2. Extract (cache-aware)
Reuse `data/extracted/<account>-extracted.txt` if present. Otherwise run:
```bash
python3 agent/extract.py data/input/<file>.json > data/extracted/<account>-extracted.txt
```

## 3. Run the full analysis
Follow `agent/prompt.md` exactly — all phases (0–7), all output instructions, and all file creation steps. Read `.claude/rules/guardrails.md` before starting and apply all rules throughout.

The prompt defines the full output format including trace logging after each phase, the technical analysis structure, and the customer report format. Follow it as written — do not simplify or merge the three outputs into one.

## 4. Deliver
Follow the output delivery instructions at the end of `agent/prompt.md`:
- All 3 files are written to `data/output/[account]/` during the run (folder auto-created if needed)
- Present the customer report inline inside a ```markdown block (copyable)
- Do not ask where to save
