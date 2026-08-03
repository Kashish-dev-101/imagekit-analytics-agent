---
description: Pre-call health check — reports the current state of the account across traffic, formats, transform coverage, top bandwidth assets, ABS, and cache. No flags, no recommendations. Numbers only — decision is on the reader.
when_to_use: Before a customer call for a quick account snapshot, or to decide whether to run the full analysis with /analytics-run.
---

# /analytics-quickcheck — Account health check (state only)

## 1. Resolve the input
Resolve per `.claude/skills/analytics-preflight/SKILL.md`.

## 2. Extract (cache-aware)
Reuse `data/extracted/<account>-extracted.txt` if present. Otherwise:
```bash
python3 agent/extract.py data/input/<file>.json > data/extracted/<account>-extracted.txt
```

## 3. Run

Read `agent/prompt.md` and `.claude/rules/guardrails.md` before starting.

| Phase | What to run | What to skip |
|---|---|---|
| Phase 0 | Full — data integrity check | — |
| Phase 1 | Totals, daily average, trend, spike detection, top 3 countries | Referrers |
| Phase 2 | Image and video format breakdown and avg sizes | — |
| Phase 3 | Traffic mix % only — desktop browser, mobile browser, native mobile, bot/AI, server-side | Phase 2 cross-reference, per-client flag rules |
| Phase 4 | Image transform coverage % (bandwidth-based) + top 5 images by bandwidth + top 5 videos by bandwidth | Asset dimension fetching, ffprobe, video width cap checks |
| Phase 5 | Cache hit rate only | Transform strategy, sprawl, near-duplicate checks |

Also from Phase 5 data: scan `videoTransform.requestWise.items` for `sr-`, `protocol-hls`, `protocol-dash` — note ABS status.

Skip entirely: Phase 6 (top IPs), Phase 7 (VPU)

## 4. Output — state only

No ✅ / ⚠️ / 🔴 anywhere in the output.
No Recommendation lines.
No "consider", "should", or "opportunity" language.
Report numbers and state — the reader decides what to do with them.

The only exception: the data truncation warning from Phase 0, if triggered — that is a data integrity issue, not a quality judgment, and must be shown prominently.

---

```
# [Account] — Health Check
**Period:** [date range]
**Prepared:** [date]

[DATA TRUNCATION WARNING — only if Phase 0 detected it:
"formatWise and deviceDistribution breakdowns cover only X% of total traffic
(known platform data issue). Percentages below reflect the visible subset only."
Omit this block entirely if no truncation detected.]

---

## Traffic

**Total:** [X] requests / [X] TB
**Daily average:** [X] requests/day / [X] GB/day
**Trend:** growing / flat / declining
**Spike:** [date] at [X]× daily average ([X] requests, [X] GB)
— or: "No spike detected"
**Top countries:** [Country 1: X%] [Country 2: X%] [Country 3: X%]

---

## Traffic Mix

| Category                  | % of total requests |
|---------------------------|---------------------|
| Desktop browser           | X%                  |
| Mobile browser            | X%                  |
| Native mobile app         | X%                  |
| Bot / AI agent            | X%                  |
| Server-side / programmatic| X%                  |

---

## Images

| Metric              | Value                        |
|---------------------|------------------------------|
| Avg image size      | X KB                         |
| WebP                | X% of image requests         |
| AVIF                | X% of image requests         |
| JPEG                | X% of image requests         |
| PNG                 | X% of image requests         |
| Transform coverage  | X% of image bandwidth        |

Note on transform coverage: measures native `tr=` param usage only. For accounts
using a URL rewriter (Cloudinary, Akamai, Imgix) this reads near-zero regardless
of actual optimization applied — not a gap.

---

## Top 5 Images by Bandwidth

| Asset | Total bandwidth | Bandwidth/view | Views |
|-------|----------------|----------------|-------|
| [path/filename] | [X GB] | [X KB] | [X] |
| [path/filename] | [X GB] | [X KB] | [X] |
| [path/filename] | [X GB] | [X KB] | [X] |
| [path/filename] | [X GB] | [X KB] | [X] |
| [path/filename] | [X GB] | [X KB] | [X] |

---

## Video

| Metric                    | Value                                              |
|---------------------------|----------------------------------------------------|
| Avg video size            | X MB                                               |
| WebM                      | X% of video requests                              |
| MP4                       | X% of video requests                              |
| Adaptive bitrate streaming| Active (HLS · sr-[tiers]) / Active (DASH) / Not detected |

---

## Top 5 Videos by Bandwidth

| Asset | Total bandwidth | Bandwidth/view | Views |
|-------|----------------|----------------|-------|
| [path/filename] | [X TB/GB] | [X MB] | [X] |
| [path/filename] | [X TB/GB] | [X MB] | [X] |
| [path/filename] | [X TB/GB] | [X MB] | [X] |
| [path/filename] | [X TB/GB] | [X MB] | [X] |
| [path/filename] | [X TB/GB] | [X MB] | [X] |

---

## Cache

| Metric          | Value |
|-----------------|-------|
| Cache hit rate  | X%    |
```

---

## 5. Deliver
- Present inline inside a ```markdown block (copyable).
- End with: *"Want me to save this? I'll write it to `data/output/<account>/`. For findings and recommendations, run `/analytics-run`."*
- Save to `data/output/<account>/<account>-<period>-quickcheck.md` only on confirmation.
