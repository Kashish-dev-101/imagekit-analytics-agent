---
name: analytics-compare
description: Compare two equal-duration periods of ImageKit analytics for the same account — requests, bandwidth, format mix, avg object size, daily spikes, transform coverage, and traffic source shift. Factual only — reports what the data shows, not external reasons.
when_to_use: Two ImageKit analytics JSONs for the same account, any matching date range (day vs day, week vs week, month vs month).
---

# /analytics-compare — Period comparison

## 1. Resolve TWO files
Resolve per `.claude/skills/analytics-preflight/SKILL.md`. Auto-pick when exactly two JSONs are present for the account; otherwise list and ask. Skip if preflight already resolved them.

Label them:
- **Period A** — the earlier period
- **Period B** — the later period

## 2. Extract both (compare-specific folder)

Derive the extracted filename from the input JSON filename:
`acme-june-2026.json` → `data/extracted/compare/acme-june-2026-extracted.txt`

**All compare extracts go in `data/extracted/compare/` — never in `data/extracted/` directly.** That folder is the main agent's cache and must not be touched by this skill. Create `data/extracted/compare/` if it doesn't exist.

Reuse if already present. Otherwise:
```bash
mkdir -p data/extracted/compare
python3 agent/extract.py data/input/<file>.json > data/extracted/compare/<account>-<period>-extracted.txt
```

## 3. Date alignment check

Read the `period` line from each extracted file's HEADER section.

- **Durations differ by 1–2 days** (e.g. 30 vs 31 days — different month lengths): proceed. Note the difference at the top of the output.
- **Durations differ by 3 or more days**: stop.
  > "Period A covers [X days: date range]. Period B covers [Y days: date range]. This skill needs equal-duration exports to compare like-for-like. Export a [X]-day range for Period B and drop it in data/input/ — for example [suggested matching date range]."

  Do not proceed, do not slice, do not extrapolate.

## 4. Read and record

Read `.claude/rules/guardrails.md` before starting.

For **each period**, compute the following from the extracted file:

**Volume**
- `request.total`, `bandwidth.total`, number of days (from HEADER)
- Daily average requests = `request.total ÷ days`
- Daily average bandwidth = `bandwidth.total ÷ days`

**Average object size**
- From `formatWise.bandwidthWise`: sum bandwidth for all `image/*` entries → `image_bw`. Sum requests for all `image/*` entries → `image_req`. Avg image size = `image_bw ÷ image_req`.
- Same for `video/*` entries → avg video size.

**Format mix**
- From `formatWise.requestWise`: for each format, compute % of total image requests (image formats) and % of total video requests (video formats).
- Image formats: `image/webp`, `image/avif`, `image/jpeg`, `image/png`, `image/gif`
- Video formats: `video/webm`, `video/mp4`

**Transform coverage**
- `transform.bandwidthWise.bandwidth ÷ image_bw × 100`

**Cache hit rate**
- `resultType.requestWise`: Hit ÷ (Hit + Miss) × 100

**Storage**
- `storage_bytes.total`

**Daily spikes**
- From `request.dateWise`: find the peak day. Spike ratio = peak day requests ÷ daily average.
- From `bandwidth.dateWise`: find the peak day. Spike ratio = peak day bandwidth ÷ daily average.
- Record date and magnitude for any day above 2× daily average in either period.

**Top bandwidth assets**
- `topImages.bandwidthWise`: top 3 — bandwidth and bandwidth/view
- `topVideos.bandwidthWise`: top 3 — bandwidth and bandwidth/view

**Traffic source mix**
- `topUserAgent`: classify into browser / native mobile / bot / server-side using the label field. Sum request % per category.

## 5. Calculate deltas

For every metric: % change = (Period B − Period A) ÷ Period A × 100

**Flag thresholds:**

| Metric | Note | ⚠️ |
|---|---|---|
| Daily avg requests | > 10% change | > 25% change |
| Daily avg bandwidth | > 10% change | > 25% change |
| Avg image size | > 10% change | > 20% change |
| Avg video size | > 10% change | > 20% change |
| Any format's share | shift > 3 percentage points | shift > 8 percentage points |
| Transform coverage | — | shift > 5 percentage points |
| Cache hit rate | — | shift > 3 percentage points |
| Traffic source category | shift > 5 percentage points | — |

**Factual rule — strictly enforced:**
Report what the data shows and how metrics connect to each other. Do not write "likely a campaign", "probably a bot surge", "may have been a product launch", or any other external cause. If bandwidth grew and JPEG share went up, write that — not why JPEG share went up. If a spike occurred on a specific date, state the date and magnitude — do not guess what caused it.

## 6. Output — fixed structure

Exactly these sections, in this order. Do not add sections, do not reorder.

---

**[Account] — [Period A date range] vs [Period B date range]**
**Prepared:** [date]
[⚠️ Duration note if 1–2 day mismatch]

---

**TL;DR**
One sentence — the main story the numbers tell. State direction and the primary metric that drove it. Factual only.

---

**Top-Line Changes**

| Metric | Period A | Period B | Change |
|---|---|---|---|
| Requests — total | | | |
| Requests — per day | | | |
| Bandwidth — total | | | |
| Bandwidth — per day | | | |
| Avg image size | | | |
| Avg video size | | | |
| Cache hit rate | | | |
| Storage | | | |

---

**Volume Story**

State whether requests and bandwidth moved together or diverged.
- If bandwidth grew faster than requests: avg object size went up — connect to the format mix and transform coverage findings below.
- If requests grew faster than bandwidth: efficiency improved — connect to what changed in format or transform coverage.

State the mechanism from the data only. Do not state external reasons.

---

**Format Mix**

| Format | Period A % | Period B % | Change |
|---|---|---|---|
[Image formats first, then video. Only include formats with > 0% in either period.]

Flag any shift above threshold. State what a format shift implies for avg object size — not why the shift happened.

---

**Daily Spikes**

Period A: [peak date] at [X]× daily average — requests: [N], bandwidth: [X GB/TB]
Period B: [peak date] at [X]× daily average — requests: [N], bandwidth: [X GB/TB]

If no spike above 2× in a period: "No single-day spike detected in this period."

---

**Top Bandwidth Assets**

Images — top 3 each period:

| | Period A | Period B |
|---|---|---|
| #1 | [bandwidth, BW/view] | [bandwidth, BW/view] |
| #2 | | |
| #3 | | |

Flag any asset that appears in Period B but not Period A, or any existing asset whose bandwidth/view changed by more than 20%.

Videos — same format.

No raw filenames or file paths in this section — describe assets by product area (e.g. "homepage banner", "product listing thumbnail").

---

**Traffic Source Mix**

Only include this section if any category shifted more than 5 percentage points. If stable: "Traffic source mix was stable across both periods — no category shifted more than 5 percentage points."

| Category | Period A % | Period B % | Change |
|---|---|---|---|

---

**Transform Coverage**

Period A: X% | Period B: Y% | Change: ±Z percentage points [⚠️ if above threshold]

One sentence on what the coverage change implies for bandwidth — not why it changed.

---

**What the Data Doesn't Explain**

Changes the data shows but cannot attribute to any measured metric. Write as questions — one per bullet. These are the questions to take to the customer.

- "The spike on [date] in Period B had no matching spike in Period A — what happened on that date?"
- "A new top-bandwidth asset appeared in Period B that was absent in Period A — is this new content or a URL change?"

If everything in the output is explained by the data: "All changes above are accounted for by the measured metrics."

---

**What's Not the Cause**

Rule out metrics that didn't change significantly. One line each.
Example: "Cache hit rate was flat (95.1% → 95.3%) — caching is not a factor in the bandwidth change."

---

## 7. Deliver
- Present inline inside a ```markdown block (copyable).
- End with: *"Want me to save this? I'll write it to `data/output/<account>/`."*
- Save to `data/output/<account>/<account>-compare-<period-A>-vs-<period-B>.md` only on confirmation.
