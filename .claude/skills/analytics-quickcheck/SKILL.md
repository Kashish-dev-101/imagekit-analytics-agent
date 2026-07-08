---
description: Pre-call health check across all key pillars — returns the state of the account with no recommendations. Covers traffic, formats, resizing, ABS, device mix, and cache hit rate. Fast — skips asset investigation, IP lookup, and VPU.
when_to_use: Before a customer call for a quick account snapshot, or before deciding whether to run the full analysis with /analytics-run. Returns state only — no recommendations.
---

# /analytics-quickcheck — Account health check (state only)

## 1. Resolve the input
Resolve which file to use per `.claude/skills/analytics-preflight/SKILL.md`. Skip if preflight already resolved it.

## 2. Extract (cache-aware)
Reuse `data/extracted/<account>-extracted.txt` if present. Otherwise run:
```bash
python3 agent/extract.py data/input/<file>.json > data/extracted/<account>-extracted.txt
```

## 3. Run — phases from `agent/prompt.md`

Read `agent/prompt.md` and `.claude/rules/guardrails.md` before starting. Follow the analytical logic in each phase exactly as written — the only differences from a full run are which phases to include and the output mode below.

**Run these phases:**

| Phase | What to run | What to skip |
|---|---|---|
| Phase 0 | Full — data integrity check | — |
| Phase 1 | Full — traffic totals, daily trend, spikes, top countries | Referrers |
| Phase 2 | Full — image and video format delivery | — |
| Phase 3 | Traffic mix % only — classify into: desktop browser, mobile browser, native mobile app, bot/AI agent, server-side. Report % of total for each. | Phase 2 cross-reference, per-client-type flag rules |
| Phase 4 | Step 1 only — transform adoption % | All per-asset dimension fetching, video width cap checks |
| Phase 6 | Cache hit rate only — read `resultType`, compute Hit / (Hit + Miss) | Full transform strategy, sprawl analysis, near-duplicate checks |

**Also check (from Phase 6 data):**
Scan `videoTransform.items` for DASH or HLS patterns (`sr-`, `protocol-dash`, `protocol-hls`). Note whether ABS is active or not detected.

**Skip entirely:** Phase 5 (top assets), Phase 7 (top IPs), Phase 8 (VPU)

## 4. Output mode — state only

Report ✅ / ⚠️ / 🔴 status for each metric. **Do not include any Recommendation lines.** This report shows where the account stands — recommendations come from `/analytics-run`.

One short MD, structured as:

```
# [Account] — Health Check
**Period:** [date range]

[⚠️ Data truncation warning if applicable — Phase 0]

## Traffic
[Totals, trend, spike with avg object size on spike day, top countries]

## Traffic Mix
[% breakdown table: desktop browser / mobile browser / native mobile / bot / server-side]

## Images
| Metric | Value | Status |
|---|---|---|
| Avg image size | X KB | — |
| Format delivery | WebP X% / AVIF X% / JPEG X% | ✅/⚠️ |
| Transform adoption | X% | ✅/⚠️/🔴 |

## Video
| Metric | Value | Status |
|---|---|---|
| Avg video size | X MB | — |
| Format delivery | WebM X% / MP4 X% | ✅/⚠️ |
| Transform adoption | X% | ✅/⚠️/🔴 |
| Adaptive bitrate streaming | Active / Not detected | ✅/⚠️ |

## Cache
| Cache hit rate | X% | ✅/⚠️ |
```

## 5. Deliver
- Present inline inside a ```markdown block (copyable).
- End with: *"Want me to save this? I'll write it to `data/output/<account>/`. Want the full analysis with recommendations? Run `/analytics-run`."*
- Write to `data/output/<account>/<account>-<period>-quickcheck.md` only if the user confirms.
