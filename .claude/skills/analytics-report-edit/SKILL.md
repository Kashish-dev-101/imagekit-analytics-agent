---
name: analytics-report-edit
description: Make safe edits to an existing customer analytics report — tone, wording, reprioritisation. Never re-runs the analysis and never touches source data. Use for post-run changes to a finished report.
when_to_use: User wants to revise a finished analytics report, not re-run it.
---

# /analytics-report-edit — Safe report edits

## 1. Resolve the report
Resolve the report file per `.claude/skills/analytics-preflight/SKILL.md` (by account hint in `data/output/`, or wherever the user saved it — auto-pick when one match, else ask). Skip if preflight already resolved it.

## 2. Apply edits — within the File Protection rules
- **Only edit the report file.** Do NOT re-run any analysis phase, do NOT re-read the JSON.
- If a detailed analysis/trace file exists for this account, pull supporting data only from it; otherwise work from the report's own content.
- **If the request is ambiguous** (e.g. "change the findings", "update the analysis") — ask whether they want a full re-run (new JSON) or just report edits. Do not touch anything until answered.

## 3. Pre-save check
Before writing the file, run the Output 2 pre-save checklist from `agent/prompt.md` on the edited report. Fix any failures before saving — edits must not break the report structure, taxonomy headings, highlights format, or introduce saving estimates.

## 4. Deliver
- Present the updated report inline inside a ```markdown block (copyable).
- Save back to the same file and confirm the path.
