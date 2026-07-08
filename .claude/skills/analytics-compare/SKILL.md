---
description: Compare two periods of ImageKit analytics for one account (month-over-month diff) and produce a single high-level MD — what changed, the root cause, and a recommendation. Use when the user has two analytics JSONs to compare.
when_to_use: Two ImageKit analytics JSONs for the same account, different periods, in data/input/.
---

# /analytics-compare — Month-over-month diff (single MD)

## 1. Resolve TWO files
Resolve the two files per `.claude/skills/analytics-preflight/SKILL.md` (auto-pick when exactly two are clear, else list and ask for the two; periods read and stated from each file). Skip if preflight already resolved them.

## 2. Extract both (cache-aware)
- For each file, reuse `data/extracted/<…>-extracted.txt` if present, else run `agent/extract.py` (see other skills for the command).

## 3. Check date alignment before comparing
Read the `period` line from each extracted file's HEADER section. If the two exports cover **different numbers of days or different date ranges**, stop and call it out:

> "Period A covers [X days: date range]. Period B covers [Y days: date range]. These don't align — the comparison won't be like-for-like. Can you provide exports for the same date range? If you want to proceed anyway, I'll compare on the basis of the shorter period ([N days])."

Do not extrapolate or normalise. Wait for the user's answer before continuing.

If the user confirms to proceed: restrict the comparison to the number of days in the shorter export (use the daily trend data to identify the overlapping window) and state clearly at the top of the output which date range was used.

## 4. Compare
- Read `.claude/rules/guardrails.md` for metric definitions and saving ranges.
- Compare across both periods: requests, bandwidth, storage; format mix (WebP / AVIF / JPEG / PNG, WebM / MP4); transform adoption %; cache hit rate; top origins / endpoints; per-view sizes; passthrough / no-transform share.
- Identify the biggest driver(s) of any change and the most likely root cause.

## 5. Output — one high-level MD
- **TL;DR** — the one-line story
- **Key numbers** — table: period A vs B, change %
- **Root cause** — what's actually driving the change
- **What's NOT the cause** — rule out the obvious (bigger images, worse formats, etc.)
- **Recommendation**

## 6. Deliver
- Present inline inside a ```markdown block (copyable).
- End with: *"Want me to save this? I'll write it to `data/output/<account>/`."*
- Write to `data/output/<account>/<account>-compare-<A>-vs-<B>.md` only if the user confirms.
