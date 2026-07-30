# extract.py — Reference

## Purpose

`extract.py` takes a raw ImageKit analytics JSON export and flattens it into a compact text file. The goal is to reduce token usage when passing data to the analytics agent while preserving every analytically useful data point.

It is a **structural flattener only** — it does not calculate, convert, aggregate, or summarise anything. All values come directly from the JSON exactly as they appear.

---

## What it does

1. Reads a single analytics JSON from `data/input/`
2. Flattens nested structures into labelled lines
3. Sorts list items by count or bandwidth (descending) for readability
4. Outputs to stdout → piped to `data/extracted/<account>-extracted.txt`

**Command:**
```bash
python3 agent/extract.py data/input/<file>.json > data/extracted/<account>-extracted.txt
```

The skills check for an existing extracted file before running — if `data/extracted/<account>-extracted.txt` exists, it reuses it.

---

## JSON schema handled

The analytics JSON uses a nested structure where most fields are wrapped in `{requestWise, bandwidthWise}` sub-objects. The extractor handles both sub-objects for every field that has them.

Fields present in the JSON:

| Field | Structure | Notes |
|---|---|---|
| `request` | `{total, dateWise, pattern}` | Top-level totals and daily trend |
| `bandwidth` | `{total, dateWise, pattern}` | Same structure as request |
| `storage_bytes` | `{total}` | May be empty `{}` — handled gracefully |
| `storage` | `{dateWise: [{date, avgUploadStorage, avgOriginalCacheStorage}]}` | Daily avg storage |
| `formatWise` | `{requestWise: [...], bandwidthWise: [...]}` | All MIME types served — images, video, JS, CSS, fonts, audio, PDFs and more. Filter by `name` prefix when computing image-only or video-only totals (`image/`, `video/`). |
| `statusCodeWise` | `{requestWise: [...], bandwidthWise: [...]}` | requestWise items have no bandwidth field |
| `errorCodeWise` | flat list `[{name, count}]` | Not wrapped — exception to the pattern |
| `resultType` | `{requestWise: [...], bandwidthWise: [...]}` | Cache hit/miss/error |
| `country` | `{requestWise: {count, bandwidth, items}, bandwidthWise: {count, bandwidth, items}}` | Items nested one level deeper |
| `referral` | `{requestWise: {items}, bandwidthWise: {items}}` | Items nested inside sub-object |
| `topUserAgent` | `{requestWise: [...], bandwidthWise: [...]}` | All 50 items, both views |
| `browserDistribution` | `{requestWise: [...], bandwidthWise: [...]}` | |
| `deviceDistribution` | `{requestWise: [...], bandwidthWise: [...]}` | Granular device breakdown (e.g. "Smartphone - Apple iPhone") |
| `transform` | `{requestWise: {count, bandwidth, items}, bandwidthWise: {count, bandwidth, items}}` | All transform strings |
| `videoTransform` | Same as transform | |
| `topImages` | `{bandwidthWise: [{url, bandwidth, views}], requestWise: [{url, bandwidth, views}]}` | All 50 items |
| `topVideos` | Same as topImages | |
| `topOthers` | `{bandwidthWise: [...], requestWise: [...]}` | Non-image, non-video assets |
| `top404` | `{t404: [{url, views}]}` | All items |
| `topIps` | `{requestWise: [...], bandwidthWise: [...]}` | All 50 items |
| `videoProcessingUnits` | `{total, dateWise: [{date, vpuUsage: {SD, HD, 4K, 8K, 16K}}]}` | Only days with usage > 0 are printed |
| `extensionUnits` | `{total, extensionWiseOperations: {key: count}}` | Only non-zero operations printed |

---

## What it keeps vs drops

**Kept — all analytical data:**
- All counts and bandwidth values as raw integers (bytes, not GB)
- Full URLs for every top image, video, and 404 — needed for pattern analysis
- All transform strings — full strings, not truncated
- All user agent strings — full strings
- Both requestWise and bandwidthWise views for every field that has them
- Daily trend for requests and bandwidth
- Daily storage averages
- VPU breakdown by resolution tier
- Extension unit operations by type

**Dropped — display/UI metadata only:**
- `thumbnailUrl` on topImages and topVideos (IK proxy URLs used only in the analytics dashboard UI)
- `fillColor` on chart datasets (chart rendering metadata)
- `savingsTrend` dateWise array (bandwidth saving estimates by day — not used in analysis)
- `networkDistribution` and `original_cache_storage_bytes` (empty in all observed JSONs)
- `_id` and `_meta.backend` are included in the header for reference

---

## Token savings

Tested on two accounts (May 2026):

| Account | Raw JSON | Extracted text | Saving |
|---|---|---|---|
| Small (acme) | ~150 KB / ~38K tokens | ~73 KB / ~18K tokens | ~51% |
| Large (Story, 25M requests) | ~214 KB / ~54K tokens | ~109 KB / ~27K tokens | ~49% |

The saving comes from removing JSON structural overhead (brackets, repeated key names, commas) and the display-only fields above. The extracted text size scales with number of distinct items (top-50 lists, UA list, transform strings) rather than raw request volume — so a 25M request account doesn't produce a dramatically larger file than a small one.

---

## Debugging

If the extractor crashes on a new JSON, the most likely causes are:

1. **New field added to the JSON** — check what top-level keys are present:
   ```python
   import json; d = json.load(open('file.json')); print(list(d.keys()))
   ```
2. **`requestWise` or `bandwidthWise` missing on a field** — the extractor uses `.get()` throughout so it degrades gracefully, but check the section that failed
3. **`storage_bytes` empty** — handled with `.get('total', 'N/A')`, should not crash
4. **New sub-structure** — if a field that was a flat list becomes a wrapped object (or vice versa), update the relevant section in `extract.py`

The extractor was rewritten in June 2026 to match the current JSON schema (all major fields wrapped in `{requestWise, bandwidthWise}`). The original version assumed flat lists and broke on the new schema.
